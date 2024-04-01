#!/usr/bin/env bash
awslocal s3 mb s3://ums
awslocal ses verify-email-identity --email internship@innowise.com --region us-east-2 --endpoint-url=http://localstack-service:4566