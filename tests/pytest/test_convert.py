"""This testing class is an integration test suite.
What it does is consider one of the demo scenarios and test whether we can obtain the same results with the refactored code
"""

import os
import sys

import pytest

sys.path.append("./tests/")
sys.path.append("./tests/refactor-tests/")

from palimpzest.constants import Model, PromptStrategy
from palimpzest.core.elements.records import DataRecord
from palimpzest.core.lib.schemas import File, TextFile
from palimpzest.datamanager.datamanager import DataDirectory
from palimpzest.query.operators.convert import LLMConvertBonded, LLMConvertConventional
from palimpzest.query.operators.datasource import MarshalAndScanDataOp

if not os.environ.get("OPENAI_API_KEY"):
    from palimpzest.utils.env_helpers import load_env

    load_env()


@pytest.mark.parametrize("convert_op", [LLMConvertBonded, LLMConvertConventional])
def test_convert(convert_op, email_schema, enron_eval_tiny):
    """Test whether convert operators"""
    model = Model.GPT_4o
    scan_op = MarshalAndScanDataOp(output_schema=TextFile, dataset_id=enron_eval_tiny)
    convert_op = convert_op(
        input_schema=File,
        output_schema=email_schema,
        model=model,
        prompt_strategy=PromptStrategy.COT_QA,
    )
 
    datasource = DataDirectory().get_registered_dataset(enron_eval_tiny)
    candidate = DataRecord(schema=File, source_id=0)
    candidate.idx = 0
    candidate.get_item_fn = datasource.get_item

    # run DataSourcePhysicalOp on record
    outputs = []
    record_set = scan_op(candidate)
    for record in record_set:
        output = convert_op(record)
        outputs.extend(output.data_records)

    for record in outputs:
        print(record.sender, record.subject)
