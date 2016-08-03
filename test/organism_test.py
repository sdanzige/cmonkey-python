
"""organism_test.py - unit tests for organism module

This file is part of cMonkey Python. Please see README and LICENSE for
more information and licensing details.
"""
import unittest
import cmonkey.util as util
import cmonkey.network as nw
import cmonkey.organism as org
import cmonkey.seqtools as st


SEARCH_DISTANCES = {'upstream':(-20, 150)}
SCAN_DISTANCES = {'upstream':(-30, 250)}


class MockRsatDatabase:
    """mock RsatDatabase"""

    def __init__(self, html):
        self.html = html

    def get_directory(self):
        """returns the directory listing's html text"""
        return self.html

    def get_taxonomy_id(self, _):
        """returns a simulation of the organism_names.tab file"""
        return "4711"

    def get_rsat_organism(self, _):
        return 'Halobacterium_sp'

    def get_features(self, _):
        """returns a fake feature.tab file"""
        return ('-- comment\n' +
                'NP_206803.1\tCDS\tnusB\tNC_000915.1\t123\t456\tD\n' +
                'NP_206804.1\tCDS\tnusC\tNC_000915.1\t234\t789\tR\n')

    def get_feature_names(self, _):
        """returns a fake feature_names.tab file"""
        return ("-- comment\nNP_206803.1\tNP_206803.1\tprimary\n" +
                "NP_206803.1\tVNG12345G\talternate\n" +
                "gene1\talt1\talternate")

    def get_contig_sequence(self, organism, contig):
        """return a contig sequence"""
        return "ACGTTTAAAAGAGAGAGAGACACAGTATATATTTTTTTAAAA"


class MockMicrobesOnline:
    def get_operon_predictions_for(self, organism_id):
        with open('testdata/gnc64091.named') as infile:
            return infile.read()


class MicrobeTest(unittest.TestCase):  # pylint: disable-msg=R0904
    """Test class for Organism"""

    def setUp(self):  # pylint: disable-msg=C0103
        """test fixture"""
        self.mockFactory = MockNetworkFactory()
        self.organism = org.Microbe('hal', 'Halobacterium SP',
                                    org.RsatSpeciesInfo(MockRsatDatabase(''),
                                                        'hal',
                                                        'Halobacterium_SP',
                                                        12345),
                                    12345,
                                    MockMicrobesOnline(),
                                    [self.mockFactory],
                                    SEARCH_DISTANCES,
                                    SCAN_DISTANCES)

    def test_init_genome(self):
        """Tests the init_genome() method"""
        organism = self.organism
        scan_seqs = organism.sequences_for_genes_scan(['VNG12345G'], seqtype='upstream')
        self.assertEquals((st.Location('NC_000915.1', -128, 152, False),
                           'ACGTTTAAAAGAGAGAGAGACACAGTATATATTTTTTTAAAA'),
                          scan_seqs['NP_206803.1'])
        search_seqs = organism.sequences_for_genes_search(['VNG12345G'], seqtype='upstream')
        self.assertEquals((st.Location('NC_000915.1', -28, 142, False),
                           'ACGTTTAAAAGAGAGAGAGACACAGTATATATTTTTTTAAAA'),
                          search_seqs['NP_206803.1'])

    def test_search_no_operons(self):
        """Tests the init_genome() method"""
        organism = self.organism
        organism.use_operons = False
        scan_seqs = organism.sequences_for_genes_scan(['VNG12345G'], seqtype='upstream')
        self.assertEquals((st.Location('NC_000915.1', -128, 152, False),
                           'ACGTTTAAAAGAGAGAGAGACACAGTATATATTTTTTTAAAA'),
                          scan_seqs['NP_206803.1'])

    def test_get_networks(self):
        """tests the networks() method"""
        organism = self.organism
        networks = organism.networks()
        self.assertEquals(1, len(networks))
        self.assertEquals(organism, self.mockFactory.create_called_with)


class MockNetworkFactory:
    """a mock NetworkFactory"""
    def __init__(self):
        self.create_called_with = None

    def __call__(self, organism, ratios):
        self.create_called_with = organism
        return nw.Network.create('network', [], 0.0, check_size=False)
