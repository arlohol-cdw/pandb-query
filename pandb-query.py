import argparse
from pan.xapi import *

# TODO Send Bad URLS to different file
# TODO Output CloudDB as well as local DB definition


def make_parser():
    # Parse the arguments
    parser = argparse.ArgumentParser(description="Bulk PAN-DB URL lookup utility")
    parser.add_argument("-u", "--username", help="administrator username")
    parser.add_argument("-p", "--password", help="administrator password")
    parser.add_argument("-f", "--firewall", help="firewall hostname or IP address")
    parser.add_argument("-t", "--tag", help="firewall tag from the .panrc file", default='')
    parser.add_argument("-i", "--infile", help="input file of URLs", default='')
    parser.add_argument("-o", "--outfile", help="output file", default='')
    args = parser.parse_args()
    return args


def read_file(filename):
    try:
        infilehandle = open(filename, 'r')
        return infilehandle
    except IOError:
        print("Error: Cannot open file %s" % filename)


def write_file(filename):
    try:
        outfilehandle = open(filename, 'w')
        return outfilehandle
    except IOError:
        print("Error: Cannot open file %s" % filename)


def make_key(username, password, firewall):
    newconn = PanXapi(api_username=username, api_password=password, hostname=firewall)
    newconn.keygen()
    return newconn


def get_url(fwconn, url):
    try:
        fwconn.op(cmd="<test><url>%s</url></test>" % url)
    except PanXapiError:
        print('Bad URL: ', url)
    return fwconn


def make_pretty(elem):
    try:
        result = elem.text.split('\n')
        local = result[1]
        cloud = result[2]
    except AttributeError:
        return 'not-resolved'
    local_category = local.split(' ')[1]
    cloud_category = cloud.split(' ')[1]
    return local_category, cloud_category


def main():
    # Grab the args

    myargs = make_parser()

    # Open the input file
    if myargs.infile:
        infile = read_file(myargs.infile)
    else:
        infile = sys.stdin

    # Open the output file
    if myargs.outfile:
        outfile = write_file(myargs.outfile)
    else:
        outfile = sys.stdout

    # Open a firewall API connection
    if myargs.tag:
        # Use the .panrc API key
        myconn = PanXapi(tag=myargs.tag)
    else:
        # Generate the API key
        myconn = make_key(myargs.username, myargs.password, myargs.firewall)

    # Iterate through the URL list, perform the lookup, and print the result
    outfile.write('URL,Local Category,Cloud Category')
    for myurl in infile:
        get_url(myconn, myurl.strip())
        local_cat, cloud_cat = make_pretty(myconn.element_result)
        outfile.write(f'{myurl.strip()},{local_cat},{cloud_cat}')
        outfile.flush()

    # Close the input file
    if infile is not sys.stdin:
        infile.close()

    # Close the output file
    if outfile is not sys.stdout:
        outfile.close()


if __name__ == '__main__':
    main()
