import os
import sys
sys.path.append('..')
from pathlib import Path
from src.content_provider import PapersWithCodeContentProvider
from src.reporter import Reporter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from src.data_storage import DataStorage
load_dotenv("../.env")



def create_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set base logger level

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler('logfile.log')
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger



def main():

    # Logging
    logger = create_logger("test_logger")

    # Chain
    prompt = PromptTemplate(
        input_variables=["paper"],
        template=Path("../prompts/bot.prompt").read_text(),
    )

    llm = ChatOpenAI(temperature=0)

    chain = LLMChain(llm=llm, prompt=prompt)

    # Content Provider
    contentProvider = PapersWithCodeContentProvider()

    # Reporter
    data_storage = DataStorage("data")
    reporter = Reporter(content_providers=[contentProvider], llm_chain=chain, logger=logger, data_storage=data_storage)
    reports = reporter.report()

if __name__ == "__main__":
    main()