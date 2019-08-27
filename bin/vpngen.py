#!/usr/bin/env python3

from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators
import sys
import os
import ConfigParser
import urllib2

@Configuration(type='reporting')
class VPNGenCommand(GeneratingCommand):

    def generate(self):

        proxies = {'http': None, 'https': None}

        try:
            cf = ConfigParser.ConfigParser()
            cf.read(os.path.join(os.environ['SPLUNK_HOME'], 'etc/apps/VPNgen/local/vpngen.conf'))

            if cf.has_section('proxies'):
                if cf.has_option('proxies', 'https'):
                    if len(cf.get('proxies', 'https')) > 0:
                        proxies['https'] = cf.get('proxies', 'https')

        except:
            pass

        if proxies['https'] is not None:
            proxy = urllib2.ProxyHandler(proxies)
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)

        try:
            url = urllib2.urlopen("https://raw.githubusercontent.com/ejrv/VPNs/master/vpn-ipv4.txt")
        except:
            raise Exception("Please check app proxy settings")

        if url.getcode()==200:

            for line in url.read().split('\n'):
                if line.startswith('#') or not line:
                    # ignore blank lines and lines starting with #
                    continue
                if '/' not in line:
                    # CIDR notation
                    line = line.strip() + '/32'
                
                yield {'ip': line, 'vpn': 'true'}
                
        else:
            raise Exception("Received response: " + url.getcode())

dispatch(VPNGenCommand, sys.argv, sys.stdin, sys.stdout, __name__)
