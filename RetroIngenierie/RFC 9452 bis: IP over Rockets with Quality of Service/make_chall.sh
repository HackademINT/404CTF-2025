#!/bin/bash

rm rfc.zip
cargo b
cp target/debug/http-over-rockets .
zip rfc .env http-over-rockets static/* templates/*
rm http-over-rockets
