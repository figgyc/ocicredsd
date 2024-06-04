#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64, os, socket, socketserver
import oci

socket_file_path = os.environ.get("SOCKET_PATH", "/run/ocicredsd/ocicredsd.sock")

LISTEN_FDS = int(os.environ.get("LISTEN_FDS", 0))
OCI_VAULT_ID = os.environ.get("OCI_VAULT_ID")

region = OCI_VAULT_ID.split('.')[3]

signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
secrets_client = oci.secrets.SecretsClient(config={'region': region}, signer=signer)

def get_secret_oci(secret):
    bundle = secrets_client.get_secret_bundle_by_name(secret, OCI_VAULT_ID)
    encoded_secret = bundle.data.secret_bundle_content.content.encode('ascii')
    secret = base64.b64decode(encoded_secret)
    return secret

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        secret = self.request.getpeername().split(b"/")[-1].decode('ascii')
        data = get_secret_oci(secret)
        self.request.send(data)
        self.request.close()

class UnixServer(socketserver.UnixStreamServer):
    def server_bind(self):
        if LISTEN_FDS == 0:
            socket_dir = os.path.dirname(socket_file_path)
            os.makedirs(socket_dir, exist_ok=True)
            socketserver.UnixStreamServer.server_bind(self)
        else:
            self.socket = socket.fromfd(3, self.address_family, self.socket_type)

server = UnixServer(socket_file_path, RequestHandler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Got ctrl-c, quitting")
    server.shutdown()
    os.remove(socket_file_path)