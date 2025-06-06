#!/usr/bin/env python3
"""
Initialization script to set up the Financial Research Assistant environment.
"""

import os
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories for the application."""
    directories = [
        "data",
        "data/agent_states",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def check_environment_variables():
    """Check if required environment variables are set."""
    load_dotenv()
    
    required_vars = [
        "OPENAI_API_KEY"
    ]
    
    optional_vars = [
        "NEWS_API_KEY",
        "ALPHA_VANTAGE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.warning("Please set these variables in a .env file or in your environment.")
    else:
        logger.info("All required environment variables are set.")
    
    missing_optional = []
    for var in optional_vars:
        if not os.environ.get(var):
            missing_optional.append(var)
    
    if missing_optional:
        logger.info(f"Missing optional environment variables: {', '.join(missing_optional)}")
        logger.info("These are not required but will enhance functionality if provided.")

def create_env_template():
    """Create a template .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        with open(".env.template", "w") as f:
            f.write("""# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional but recommended
NEWS_API_KEY=your_news_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
""")
        logger.info("Created .env.template file. Copy to .env and fill in your API keys.")

def main():
    """Main function to initialize the application."""
    parser = argparse.ArgumentParser(description="Initialize the Financial Research Assistant environment.")
    parser.add_argument("--check-env", action="store_true", help="Check environment variables")
    parser.add_argument("--create-dirs", action="store_true", help="Create necessary directories")
    parser.add_argument("--all", action="store_true", help="Perform all initialization tasks")
    
    args = parser.parse_args()
    
    # If no arguments provided or --all is used, do everything
    do_all = args.all or not (args.check_env or args.create_dirs)
    
    if args.create_dirs or do_all:
        create_directories()
    
    if args.check_env or do_all:
        check_environment_variables()
        create_env_template()
    
    logger.info("Initialization complete.")

if __name__ == "__main__":
    main() 