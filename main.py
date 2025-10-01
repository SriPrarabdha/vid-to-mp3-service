# main.py at the project root

import uvicorn
import os
# import pysqlite3
import sys

from dotenv import load_dotenv
import argparse
load_dotenv()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Which service to run on which port?",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '--service',
        choices=['auth', 'notification', 'convert'],
        required=True,
        help="The service to run. Must be either 'auth' or 'notification' or 'convert."
    )

    parser.add_argument(
        '--port',
        type=int, 
        required=True,
        help="On which port to run the service."
    )

    args = parser.parse_args()
    
    if args.service == 'auth':
        uvicorn.run("app.auth_service.main:app", host="0.0.0.0", port=args.port, loop="asyncio")
    elif args.service == 'notification':
        uvicorn.run("app.notification.main:app", host="0.0.0.0", port=args.port, loop="asyncio")
    elif args.service == 'convert':
        uvicorn.run("app.convert.main:app", host="0.0.0.0", port=args.port, loop="asyncio")
    else:
        raise NotImplementedError(f"Error: Unhandled service type: {args.service}")