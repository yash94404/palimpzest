.. Palimpzest documentation master file, created by
   sphinx-quickstart on Fri Jan 24 17:49:21 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. .. image:: https://palimpzest-workloads.s3.us-east-1.amazonaws.com/palimpzest-cropped.png
..    :alt: Palimpzest Logo
..    :align: center

PZ: Optimizing Pipelines of Semantic Operators
==============================================

|arXiv| |Colab| |Talk| |PyPI| |Downloads| |Github|

Palimpzest (PZ) provides a high-level, declarative interface for composing and executing pipelines of semantic operators. PZ's optimizer can automatically improve the performance of these pipelines, enabling programmers to focus on the high-level design of their pipelines.

Getting Started
---------------

You can find a stable version of the Palimpzest package on PyPI: |PyPI|. To install the package, run:

.. code-block:: console

   $ pip install palimpzest


Alternatively, to install the latest version of the package from source, you can clone `our repository <https://github.com/mitdbg/palimpzest>`_ and run the following commands:

.. code-block:: console

   $ git clone git@github.com:mitdbg/palimpzest.git
   $ cd palimpzest
   $ pip install .

.. note::

   This project is under active development.

Chat Demo
---------
To access our chat demo please go to this webpage `Palimpchat <http://3.213.4.62:8888/>`_.

Quickstart
-----------
The easiest way to get started with Palimpzest, is to run our demo in Colab: |Colab|. We demonstrate the workflow of working with PZ, including registering a dataset, composing and executing a pipeline, and accessing the results.

For eager readers, the code in the notebook can be found in the following condensed snippet. However, we do suggest reading the notebook as it contains more insight into each element of the program.

.. code-block:: python

   import pandas as pd
   import palimpzest.datamanager.datamanager as pzdm
   from palimpzest.sets import Dataset
   from palimpzest.policy import MinCost, MaxQuality
   from palimpzest.query.processor.config import QueryProcessorConfig

   # register dataset
   dataset_path = "testdata/enron-tiny"
   dataset_name = "enron-tiny"
   pzdm.DataDirectory().register_local_directory(dataset_path, dataset_name)

   # define the fields we wish to compute
   email_cols = [
      {"name": "sender", "type": str, "desc": "The email address of the sender"},
      {"name": "subject", "type": str, "desc": "The subject of the email"},
      {"name": "date", "type": str, "desc": "The date the email was sent"},
   ]

   # lazily construct the computation to get emails about holidays sent in July
   dataset = Dataset(dataset_name).sem_add_columns(email_cols)
   dataset = dataset.sem_filter("The email was sent in July")
   dataset = dataset.sem_filter("The email is about holidays")

   # execute the computation
   policy = MinCost()
   config = QueryProcessorConfig(policy=policy, verbose=True)
   output = dataset.run(config)

   # display output (if using Jupyter, otherwise use print(output_df))
   output_df = output.to_df(project_cols=["date", "sender", "subject"])
   display(output_df)

Next Steps
----------
Stay tuned for more walkthroughs and tutorials on how to use PZ! In the meantime, the main content of our documentation can be found below:

Contents
--------
.. toctree::
   :maxdepth: 1

   usage
   dataset
   policy
   datasource
   schema
   field


.. |arXiv| image:: https://img.shields.io/badge/Paper-arXiv-b31b1b?logo=arxiv
   :target: https://arxiv.org/pdf/2405.14696
   :alt: arXiv

.. |Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1zqOxnh_G6eZ8_xax6PvDr-EjMt7hp4R5?usp=sharing
   :alt: Colab

.. |Talk| image:: https://img.shields.io/badge/YouTube-Talk-red?logo=youtube
   :target: https://youtu.be/T8VQfyBiki0?si=eiph57DSEkDNbEIu
   :alt: Talk

.. |PyPI| image:: https://img.shields.io/pypi/v/palimpzest
   :target: https://pypi.org/project/palimpzest/color=green
   :alt: PyPI

.. |Downloads| image:: https://img.shields.io/pypi/dm/palimpzest
   :target: https://pypi.org/project/palimpzest/
   :alt: PyPI - Downloads

.. |GithubStars| image:: https://img.shields.io/github/stars/mitdbg/palimpzest?style=flat&logo=github
   :target: https://github.com/mitdbg/palimpzest
   :alt: Code

.. |Github| image:: https://img.shields.io/badge/GitHub-Code-blue?logo=github
   :target: https://github.com/mitdbg/palimpzest
   :alt: Code
