#!/bin/env python3 
from base64 import b64encode
from os import environ
from json import dumps
from os.path import exists, join
from sys import stderr, stdout
from string import Template

def slurp(filename, as_template=True):
    with open("cloud-config/" + filename, "r") as config:
        if as_template:
            # parse a YAML file and replace ${VALUE}s
            buffer = Template(config.read()).safe_substitute(environ)
        else:
            buffer = config.read()
    return b64encode(bytes(buffer, 'utf-8')).decode()

ADMIN_USERNAME = environ['ADMIN_USERNAME']
OWN_PUBKEY = join(environ['HOME'],'.ssh','id_rsa.pub')
GEN_PUBKEY = 'keys/' + ADMIN_USERNAME + '.pub'

if (environ.get('OWN_KEY','false').lower() == 'true') and exists(OWN_PUBKEY):
    admin_public_key = open(OWN_PUBKEY,'r').read()
    stderr.write('Warning: using %s instead of freshly generated keys.\n' % OWN_PUBKEY)
elif exists(GEN_PUBKEY):
    admin_public_key = open(GEN_PUBKEY,'r').read()
else:
    stderr.write('No public keys found, exiting.\n')
    exit(1)

params = {
    "adminUsername": {
        "value": ADMIN_USERNAME
    },
    "adminPublicKey": {
        "value": admin_public_key
    },
    "serverCustomData": {
        "value": slurp("server.yml")
    }
}

stdout.write(dumps(params, indent=4))
