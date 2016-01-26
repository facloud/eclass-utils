#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
import os
import re
import sys
import urllib2
import urllib
import argparse


#
# Make argument parser
#

def _make_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--course', help='Cource id', type=str,
                        dest='course_id', metavar='<Id>', required=True)
    parser.add_argument('-d', '--dest', help='Destination directory path',
                        type=str, dest='dest_dir_path', metavar='<Path>',
                        default='./')
    parser.add_argument('-r', '--dir', help='Remote directory path',
                        type=str, dest='remote_dir_path', metavar='<Path>')
    return parser


#
# Read user name and password
#

def _get_creds():
    try:
        username = raw_input('Username: ')
        password = raw_input('Password: ')
    except KeyboardInterrupt:
        print
        sys.exit(1)
    return username, password


#
# Gets a cookie after logging in
#

def _get_cookie(username, password):
    # Get original cookie
    f = urllib2.urlopen('http://eclass.uoa.gr')
    if f is None or f.code / 100 != 2:
        return None
    msg = f.info()
    f.close()

    # Extract Set-Cookie
    if not msg.getheaders('Set-Cookie'):
        return None
    cookie_parts = msg.getheaders('Set-Cookie')[0].split('; ')
    cookie_str = '; '.join(cookie_parts[:-1])

    # Authenticate
    data = urllib.urlencode(
        [
            ('uname', username),
            ('pass', password),
            ('submit', 'Είσοδος')
        ]
    )
    req = urllib2.Request('http://eclass.uoa.gr', data)
    req.add_header('Accept', 'text/html')
    req.add_header('Cookie', cookie_str)
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36'
        + ' (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'
    )

    # Run request
    f = urllib2.urlopen(req)
    if f is None or f.code / 100 != 2:
        return None

    return cookie_str


#
# URL extractor
#

def _get_file_urls(course_id, remote_dir_path, cookie_str):
    # Make directory URL
    url = 'http://eclass.uoa.gr/modules/document/index.php?course=%s' \
        % course_id
    if remote_dir_path is not None:
        url += '&openDir=%s' % remote_dir_path

    # Get HTML
    req = urllib2.Request(url)
    req.add_header('Accept', 'text/html')
    req.add_header('Cookie', cookie_str)
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36'
        + ' (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'
    )
    resp = urllib2.urlopen(req)
    if resp is None or resp.code / 100 != 2:
        return []
    html_str = resp.read()
    resp.close()

    # Compile regular expression
    reg_exp = re.compile(
        r'href=\'/modules/document/index\.php\?course=([A-Z0-9]*)'
        + r'&amp;download=([/a-zA-Z0-9\.]*)\'',
        re.MULTILINE & re.UNICODE & re.VERBOSE
    )

    # Run regular expressions
    matches = re.findall(reg_exp, html_str)
    if matches is None:
        return []

    ret_val = []
    for course_id, path in matches:
        if path == '/' or path == remote_dir_path:  # ignore top level
            continue
        url = 'http://eclass.uoa.gr/modules/document/index.php'
        url += '?course=%s&download=%s' % (course_id, path)
        ret_val.append(url)

    return ret_val


#
# Download file
#

def _get_filename(resp_msg):
    if not resp_msg.getheaders('Content-Disposition'):
        return None
    match = re.match(
        r'.*filename=["]?([^"]*)["]?.*',
        resp_msg.getheaders('Content-Disposition')[0],
        re.UNICODE
    )
    if match is None:
        return None
    return match.group(1).strip()


def _get_file_size(resp_msg):
    return resp_msg.getheaders('Content-Length')[0]


def _actual_download_file(resp, f, file_size):
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = resp.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r'%10d  [%3.2f%%]' % (
            file_size_dl, file_size_dl * 100. / file_size
        )
        status = status + chr(8) * (len(status) + 1)
        print status,
    print


def _download_file(url, dest_dir_path, cookie_str):
    # Make request
    req = urllib2.Request(url)
    req.add_header('Accept', 'text/html')
    req.add_header('Cookie', cookie_str)
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36'
        + ' (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'
    )

    # Run request
    resp = urllib2.urlopen(req)
    if resp.code / 100 != 2:
        return None
    msg = resp.info()

    # Get file path
    file_name = _get_filename(msg)
    file_path = os.path.join(
        os.path.abspath(dest_dir_path),
        file_name
    )

    # Open file
    f = open(file_path, 'wb')
    file_size = int(_get_file_size(msg))
    print '[INFO] Downloading: %s Bytes: %s' % (file_path, file_size)

    # Download
    _actual_download_file(resp, f, file_size)

    # Close
    f.close()
    resp.close()

    return file_path


#
# Main function
#

def main():
    # Parse arguments
    parser = _make_argument_parser()
    args = parser.parse_args()

    # Read credentials
    u, p = _get_creds()

    # Obtain cookie
    cookie_str = _get_cookie(u, p)
    if cookie_str is None:
        print '[ERROR] Login failed!'
        sys.exit(1)

    # Get download URLs
    urls = _get_file_urls(args.course_id, args.remote_dir_path, cookie_str)
    if len(urls) == 0:
        print '[ERROR] No URLs found!'
        sys.exit(1)

    # Download urls
    print '[INFO] Downloading %d URLs...' % len(urls)
    for url in urls:
        _download_file(url, args.dest_dir_path, cookie_str)

if __name__ == '__main__':
    main()
