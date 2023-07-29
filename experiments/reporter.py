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
    reporter = Reporter(content_providers=[contentProvider], llm_chain=chain, logger=logger)
    reports = reporter.report()

    logger.info(f"Reports: {len(reports)}\n\n")
    for report in reports:
        print(report)
        logger.info(f"Report: \n{report}")

if __name__ == "__main__":
    main()