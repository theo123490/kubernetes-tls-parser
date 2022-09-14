import subprocess
import yaml
import base64
import OpenSSL
import argparse
import datetime

def parse_input():
  parser = argparse.ArgumentParser()
  parser.add_argument('action')
  parser.add_argument('name' , nargs='?', const="default_name",)
  parser.add_argument("-n", "--namespace", help="namespace")
  parser.add_argument('-v', '--verbose', action='count', default=0)
  args = parser.parse_args()
  return args

def output_formatting(header, data):
  table = data
  table.insert(0, header)

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

  return result

def get_single_tls_notAfter(args):
  result = get_tls_notAfter(args)
  header = ['SECRET', 'NAMESPACE', 'DATEBEFORE']
  data = [args.name, args.namespace, str(result)]
  output_formatting(header, [data])

def get_all_tls_notAfter(args):
  cmd = "kubectl get secret --all-namespaces | grep tls"
  ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  output = ps.communicate()[0]
  secret_array = [line.decode('utf-8').split() for line in output.splitlines()]
  data = []
  for secret_line in secret_array:
    if(args.verbose>0):
      print(f"getting data from {secret_line[1]} on {secret_line[0]} ")
    args.namespace = secret_line[0]
    args.name = secret_line[1]
    data.append([args.name, args.namespace, str(get_tls_notAfter(args))])

  header = ['SECRET', 'NAMESPACE', 'DATEBEFORE']
  output_formatting(header, data)

def choose_action():
  args = parse_input()
  if(args.action == 'get_tls'):
    get_single_tls_notAfter(args)
  elif(args.action == 'get_tls_all'):
    get_all_tls_notAfter(args)
  else:
    raise ValueError("action (first argument) not found")

choose_action()
