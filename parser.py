import subprocess
import yaml
import base64
import OpenSSL
import argparse
import datetime

def parse_input():
  parser = argparse.ArgumentParser()
  parser.add_argument('action',  help="possible actions: get_tls, get_tls_all, decode_x509")
  parser.add_argument('name' , nargs='?', const="default_name", help="secret name")
  parser.add_argument("-n", "--namespace", help="namespace")
  parser.add_argument('-v', '--verbose', action='count', default=0, help="verbose")
  args = parser.parse_args()
  return args

def output_formatting(header, data):
  table = data
  table.insert(0, header)
  col_width = max(len(word) for row in table for word in row) + 2  # padding
  for row in table:
    print("".join(word.ljust(col_width) for word in row))

def get_certificate(args):
  input_string = subprocess.check_output(["kubectl", "get", "secret", args.name , "-o", "yaml", "-n", args.namespace])
  secret_yaml = yaml.safe_load(input_string)
  certificate = base64.b64decode(secret_yaml["data"]["tls.crt"])
  return certificate

def get_tls_notAfter(args):
  certificate = get_certificate(args)
  x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
  ssl_date_fmt = r'%Y%m%d%H%M%SZ'
  date_time = datetime.datetime.strptime(x509.get_notAfter().decode('ascii'), ssl_date_fmt)
  date_time = str(date_time)
  CN = x509.get_subject().CN
  CN = str(CN)
  parsed_cert = {
    'date_time': date_time,
    'CN': CN
    }
  return parsed_cert

def get_single_tls_notAfter(args):
  parsed_cert = get_tls_notAfter(args)
  header = ['SECRET', 'NAMESPACE', 'DATEBEFORE', 'CN']
  data = [args.name, args.namespace, parsed_cert['date_time'], parsed_cert['CN']]
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
    parsed_cert = get_tls_notAfter(args)
    data.append([args.name, args.namespace, parsed_cert['date_time'], parsed_cert['CN']])

  header = ['SECRET', 'NAMESPACE', 'DATEBEFORE', 'CN']
  output_formatting(header, data)

def decode_x509(args):
  certificate = get_certificate(args)
  openssl_args = ["openssl", "x509", "-text"]
  child_proccess = subprocess.Popen(openssl_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

  child_proccess.stdin.write(certificate)
  child_process_output = child_proccess.communicate()[0]

  child_proccess.stdin.close()

  print(child_process_output.decode('utf-8'))

def choose_action():
  args = parse_input()
  if(args.action == 'get_tls'):
    get_single_tls_notAfter(args)
  elif(args.action == 'get_tls_all'):
    get_all_tls_notAfter(args)
  elif(args.action == 'decode_x509'):
    decode_x509(args)
  else:
    raise ValueError("action (first argument) not found")

choose_action()
