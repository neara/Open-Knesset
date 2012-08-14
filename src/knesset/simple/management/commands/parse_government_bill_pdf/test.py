import glob
import os
import sys
from parse_government_bill_pdf import GovProposalParser
from parse_government_bill_pdf import readable as d
from util import flatten

def show_one(pdf_filename, show_details=False):
    prop = GovProposalParser(pdf_filename)
    print prop.to_unicode(show_details).encode('utf-8')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        files = sorted(glob.glob('*.pdf'))
    else:
        files = sys.argv[1:]
    for pdf_filename in files:
        if not os.path.exists(pdf_filename):
            print "no such file: %s" % (pdf_filename)
        show_one(pdf_filename, show_details=True)

