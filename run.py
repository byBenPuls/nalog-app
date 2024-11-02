import logging

from app.main import app


logging.basicConfig(
    filename="resources/logging.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Running main")
    # run_app("app.main:app")
    app.mainloop()
