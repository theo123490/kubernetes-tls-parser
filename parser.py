import subprocess
from webbrowser import get
import yaml
import base64
import OpenSSL
import argparse
import datetime

def parse_input():
  parser = argparse.ArgumentParser()
  parser.add_argument('name')
  parser.add_argument("-n", "--namespace", help="namespace")
  args = parser.parse_args()
  return args

def output_formatting(table):
  col_width = max(len(word) for row in table for word in row) + 2  # padding
  for row in table:
    print("".join(word.ljust(col_width) for word in row))

def get_tls_notAfter(args):
  input_string = subprocess.check_output(["kubectl", "get", "secret", args.name , "-o", "yaml", "-n", args.namespace])
  secret_yaml = yaml.safe_load(input_string)
  certificate = base64.b64decode(secret_yaml["data"]["tls.crt"])
  x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
  ssl_date_fmt = r'%Y%m%d%H%M%SZ'
  result = datetime.datetime.strptime(x509.get_notAfter().decode('ascii'), ssl_date_fmt)

  table =[
    ['SECRET', 'NAME', 'DATEBEFORE'],
    [args.name, args.namespace, str(result)]
  ]
  output_formatting(table)

args = parse_input()
get_tls_notAfter(args)