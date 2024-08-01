from palimpzest.planner import LogicalPlan
from .plan import LogicalPlan
from .planner import Planner

import palimpzest as pz
import palimpzest.operators as pz_ops

from itertools import permutations
from typing import List


class LogicalPlanner(Planner):
    def __init__(self, no_cache: bool=False, *args, **kwargs):
        """A given planner should not have a dataset when it's being generated, since it could be used for multiple datasets.
        However, we currently cannot support this since the plans are stored within a single planner object.
        To support this, we can use a dictionary in the form [dataset -> [Plan, Plan, ...]].
        To discuss for future versions.
        """

        super().__init__(*args, **kwargs)
        self.no_cache = no_cache

    @staticmethod
    def _compute_legal_permutations(
        filterAndConvertOps: List[pz_ops.LogicalOperator],
    ) -> List[List[pz_ops.LogicalOperator]]:
        # There are a few rules surrounding which permutation(s) of logical operators are legal:
        # 1. if a filter depends on a field in a convert's outputSchema, it must be executed after the convert
        # 2. if a convert depends on another operation's outputSchema, it must be executed after that operation
        # 3. if depends_on is not specified for a convert operator, it cannot be swapped with another convert
        # 4. if depends_on is not specified for a filter, it can not be swapped with a convert (but it can be swapped w/adjacent filters)

        # compute implicit depends_on relationships, keep in mind that operations closer to the start of the list are executed first;
        # if depends_on is not specified for a convert or filter, it implicitly depends_on all preceding converts
        for idx, op in enumerate(filterAndConvertOps):
            if op.depends_on is None:
                all_prior_generated_fields = []
                for upstreamOp in filterAndConvertOps[:idx]:
                    if isinstance(upstreamOp, pz_ops.ConvertScan):
                        all_prior_generated_fields.extend(upstreamOp.generated_fields)
                op.depends_on = all_prior_generated_fields

        # compute all permutations of operators
        opPermutations = permutations(filterAndConvertOps)

        # iterate over permutations and determine if they are legal;
        # keep in mind that operations closer to the start of the list are executed first
        legalOpPermutations = []
        for opPermutation in opPermutations:
            is_valid = True
            for idx, op in enumerate(opPermutation):
                # if this op is a filter, we can skip because no upstream ops will conflict with this
                if isinstance(op, pz_ops.FilteredScan):
                    continue

                # invalid if upstream op depends on field generated by this op
                for upstreamOp in opPermutation[:idx]:
                    for col in upstreamOp.depends_on:
                        if col in op.generated_fields:
                            is_valid = False
                            break
                    if is_valid is False:
                        break
                if is_valid is False:
                    break

            # if permutation order is valid, then add it to the list of legal permutations
            if is_valid:
                legalOpPermutations.append(opPermutation)

        return legalOpPermutations

    @staticmethod
    def _compute_logical_plan_reorderings(logical_plan: LogicalPlan) -> List[LogicalPlan]:
        """
        Given the naive logical plan, compute all possible equivalent plans with filter
        and convert operations re-ordered.
        """
        operators = logical_plan.operators
        datasetIdentifier = logical_plan.datasetIdentifier
        all_plans, op_idx = [], 0
        while op_idx < len(operators):
            op = operators[op_idx]

            # base case, if this is the first operator (currently must be a BaseScan or CacheScan)
            # then set all_plans to be the logical plan with just this operator
            if (isinstance(op, pz_ops.BaseScan) or isinstance(op, pz_ops.CacheScan)) and all_plans == []:
                all_plans = [LogicalPlan(operators=[op], datasetIdentifier=datasetIdentifier)]
                op_idx += 1

            # if this operator is not a FilteredScan or a ConvertScan: join op with each of the
            # re-orderings for its source operations
            elif not isinstance(op, pz_ops.FilteredScan) and not isinstance(op, pz_ops.ConvertScan):
                plans = []
                for subplan in all_plans:
                    new_logical_plan = LogicalPlan.fromOpsAndSubPlan([op], subplan)
                    plans.append(new_logical_plan)

                # update all_plans and op_idx
                all_plans = plans
                op_idx += 1

            # otherwise, if this operator is a FilteredScan or ConvertScan, make one plan per (legal)
            # permutation of consecutive converts and filters and recurse
            elif isinstance(op, pz_ops.FilteredScan) or isinstance(op, pz_ops.ConvertScan):
                # get list of consecutive converts and filters
                filterAndConvertOps = []
                nextOp, next_idx = op, op_idx
                while isinstance(nextOp, pz_ops.FilteredScan) or isinstance(nextOp, pz_ops.ConvertScan):
                    filterAndConvertOps.append(nextOp)
                    nextOp = operators[next_idx + 1] if next_idx + 1 < len(operators) else None
                    next_idx = next_idx + 1

                # compute set of legal permutations
                op_permutations = LogicalPlanner._compute_legal_permutations(filterAndConvertOps)

                # compute cross-product of op_permutations and subTrees by linking final op w/first op in subTree
                plans = []
                for ops in op_permutations:
                    for subplan in all_plans:
                        new_logical_plan = LogicalPlan.fromOpsAndSubPlan(ops, subplan)
                        plans.append(new_logical_plan)

                # update plans and operators (so that we skip over all operators in the re-ordering)
                all_plans = plans
                op_idx = next_idx

            else:
                raise Exception("PZ does not support the structure of this logical plan")

        return all_plans

    def _construct_logical_plan(self, dataset_nodes: List[pz.Set]) -> LogicalPlan:
        operators = []
        datasetIdentifier = None
        for idx, node in enumerate(dataset_nodes):
            uid = node.universalIdentifier()

            # Use cache if allowed
            if not self.no_cache and pz.datamanager.DataDirectory().hasCachedAnswer(uid):
                op = pz_ops.CacheScan(node.schema, cachedDataIdentifier=uid)
                operators.append(op)
                #return LogicalPlan(operators=operators)
                continue

            # first node is DataSource
            if idx == 0:
                assert isinstance(node, pz.datasources.DataSource)
                datasetIdentifier = uid
                op = pz_ops.BaseScan(datasetIdentifier=uid,outputSchema=node.schema)

            # if the Set's source is another Set, apply the appropriate scan to the Set
            else:
                inputSchema = dataset_nodes[idx - 1].schema
                outputSchema = node.schema
                if node._filter is not None:
                    op = pz_ops.FilteredScan(
                        inputSchema=inputSchema,
                        outputSchema=outputSchema,
                        filter=node._filter,
                        depends_on=node._depends_on,
                        targetCacheId=uid,
                    )
                elif node._groupBy is not None:
                    op = pz_ops.GroupByAggregate(
                        inputSchema=inputSchema,
                        outputSchema=outputSchema,
                        gbySig=node._groupBy,
                        targetCacheId=uid,
                    )
                elif node._aggFunc is not None:
                    op = pz_ops.ApplyAggregateFunction(
                        inputSchema=inputSchema,
                        outputSchema=outputSchema,
                        aggregationFunction=node._aggFunc,
                        targetCacheId=uid,
                    )
                elif node._limit is not None:
                    op = pz_ops.LimitScan(
                        inputSchema=inputSchema,
                        outputSchema=outputSchema,
                        limit=node._limit,
                        targetCacheId=uid,
                    )
                elif not outputSchema == inputSchema:
                   op = pz_ops.ConvertScan(
                        inputSchema=inputSchema,
                        outputSchema=outputSchema,
                        cardinality=pz.Cardinality(node._cardinality),
                        image_conversion=node._image_conversion,
                        depends_on=node._depends_on,
                        targetCacheId=uid,
                    )
                else:
                    raise NotImplementedError("No logical operator exists for the specified dataset construction.")

            operators.append(op)

        return LogicalPlan(operators=operators, datasetIdentifier=datasetIdentifier)

    def generate_plans(self, dataset: pz.Dataset, sentinels: bool=False) -> List[LogicalPlan]:
        """Return a set of possible logical trees of operators on Sets."""
        # Obtain ordered list of datasets
        dataset_nodes = []
        node = dataset

        while isinstance(node, pz.sets.Dataset):
            dataset_nodes.append(node)
            node = node._source
        dataset_nodes.append(node)
        dataset_nodes = list(reversed(dataset_nodes))

        if dataset_nodes[0].schema == dataset_nodes[1].schema:
            dataset_nodes = [dataset_nodes[0]] + dataset_nodes[2:]
            dataset_nodes[1]._source = dataset_nodes[0]

        if dataset_nodes[0].schema == pz.ImageFile:
            dataset_nodes[0].schema = pz.File
            dataset_nodes.insert(1, pz.sets.Dataset(source=dataset_nodes[0], schema=pz.ImageFile))
        # construct naive logical plan
        plan = self._construct_logical_plan(dataset_nodes)

        # at the moment, we only consider sentinels for the naive logical plan
        if sentinels:
            self.plans = [plan]
            return self.plans

        # compute all possible logical re-orderings of this plan
        self.plans = LogicalPlanner._compute_logical_plan_reorderings(plan)
        print(f"LOGICAL PLANS: {len(self.plans)}")

        return self.plans