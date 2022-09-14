# parser to get tls certificate expiry date time

---
# how to run

## get_tls
getting expiry date for previous tls
```bash
python parser.py get_tls $SECRET_NAME -n $NAMESPACE
```
result should looks like this
```
SECRET                           NAMESPACE                        DATEBEFORE                       CN
secret_name                      default                          2099-02-13 01:29:05              *.a.fake.domain
```
## get_tls_all
getting expiry date for all tls in cluster
```bash
 python parser.py get_tls_all
```
result should looks like this
```
SECRET                               NAMESPACE                            DATEBEFORE                           CN
this_is_a_fake_cert_name1            namespace1                            2022-08-15 02:39:09                  *.this.is.a.fake.domain
this_is_a_fake_cert_name2            namespace2                            2022-08-15 02:39:09                  *.this.is.a.fake.domain
this_is_a_fake_cert_name3            namespace3                            2022-08-15 02:39:09                  *.this.is.a.fake.domain
this_is_a_fake_cert_name4            namespace4                            2022-08-15 02:39:09                  *.this.is.a.fake.domain
this_is_a_fake_cert_name5            namespace5                            2022-08-15 02:39:09                  *.this.is.a.fake.domain
this_is_a_fake_cert_name6            namespace6                            2022-08-15 02:39:09                  *.this.is.a.fake.domain
```