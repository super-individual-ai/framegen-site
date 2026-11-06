"""Apply the 90-day retention policy to this site's dedicated Umami database."""

import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", default="docker", help="Docker executable")
    parser.add_argument("--container", default="openduckframe-analytics-db")
    args = parser.parse_args()
    # This dedicated instance contains only this site's production and test IDs.
    # No raw connection addresses or submitted feedback are stored here.
    sql = """
BEGIN;
DELETE FROM event_data WHERE created_at < now() - interval '90 days';
DELETE FROM website_event WHERE created_at < now() - interval '90 days';
DELETE FROM session_data WHERE created_at < now() - interval '90 days';
DELETE FROM session WHERE created_at < now() - interval '90 days'
  AND NOT EXISTS (SELECT 1 FROM website_event WHERE website_event.session_id = session.session_id);
COMMIT;
"""
    subprocess.run([args.docker, "exec", "-i", args.container, "psql", "-X", "-v", "ON_ERROR_STOP=1", "-U", "umami", "-d", "umami"], input=sql, text=True, check=True)


if __name__ == "__main__":
    main()
