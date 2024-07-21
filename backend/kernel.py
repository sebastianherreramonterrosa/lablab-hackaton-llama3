import os

import numpy as np
import pandas as pd
import phitter
from llama_index.core.agent.react import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.together import TogetherLLM
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")


def get_column_data(column_name: str, df: pd.DataFrame) -> list[float]:
    """
    Gets the data from a specific column of the global DataFrame.
    """
    return df[column_name].tolist()


def fit_distributions_to_data(data: list[float]) -> float:
    """
    Fit the best probability distribution to a dataset
    """
    global phitter_cont
    phitter_cont = phitter.PHITTER(data=data)
    phitter_cont.fit(n_workers=2)
    id_distribution = phitter_cont.best_distribution["id"]
    parameters = phitter_cont.best_distribution["parameters"]
    parameters_str = ", ".join([f"{k}: {v:.4g}" for k, v in parameters.items()])
    return (
        f"The best distribution is {id_distribution} with parameters {parameters_str}"
    )


def plot_histogram():
    """
    Fit the best probability distribution to a dataset
    """
    global phitter_cont
    phitter_cont.plot_histogram()
    return "showing histogram ..."


def main_backend(df: pd.DataFrame, query: str):

    get_column_tool = FunctionTool.from_defaults(
        fn=get_column_data,
        name="get_column_data",
        description="Gets the data from a specific column of the global DataFrame.",
    )
    fit_distribution_tool = FunctionTool.from_defaults(
        fn=fit_distributions_to_data,
        name="fit_distribution",
        description="Find the best probability distribution to a dataset and returns the distribution name and parameters.",
    )
    plot_histogram_tool = FunctionTool.from_defaults(
        fn=plot_histogram,
        name="plot_histogram",
        description="Plot hitogram to the current phitter process",
    )

    llm = TogetherLLM(model="meta-llama/Llama-3-70b-chat-hf", temperature=0)

    tools = [get_column_tool, fit_distribution_tool, plot_histogram_tool]
    agent = ReActAgent.from_tools(tools, llm=llm, verbose=False)

    try:
        response = agent.chat(query)

        return response
    except Exception as e:
        print(f"Error: {str(e)}")
