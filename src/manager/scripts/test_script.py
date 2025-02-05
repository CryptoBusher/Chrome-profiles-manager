from loguru import logger


def test_script(profile_name: str, _):
    logger.info(f"💩 {profile_name} - manager test script for profile  done")
