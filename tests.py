import unittest
from cages import *


test_cages_data = [
    # This next section of cages are based on problems from: https://www.janko.at/Retros/Records/LastMove/index.htm
    # In the comment, we give the author(s) and original problem. Note that multiple cages may be associated with the
    # same original problem. Lines labeled "auxiliary" are simple cages needed to verify the cage in the next
    # commented line.
    ('8/8/8/8/8/8/PPkPP3/KR1b4', [], [], 5),  # Brandis, 8/8/8/8/8/1P6/1PkPP3/KR1b4
    ('7K/pppp1ppp/4p3/8/8/8/8/8', [], [], 20),  # Ceriani, 3bkN1K/pppprp1p/4p1p1/8/8/8/8/8
    ('4B1rk/3ppKpp/8/8/8/8/8/8', [], [], 5),  # Bartolovic, Gajdos, Maslar, 4BQrk/3ppK1p/4p1p1/8/8/8/8/8
    ('4Bnrk/3ppK1p/4p1p1/8/8/8/8/8', [], [], 5),  # Same as previous
    ('2K2b2/1p1pppp1/1pp5/8/8/8/8/8', [], [], 20),  # Gajdos, 1RK1kb2/1pRpppp1/b1p5/1p6/8/8/8/8
    ('8/8/8/8/8/8/PPkPP3/K1Bb4', [], [], 5),  # Fabel, 8/8/8/8/8/P2P4/P1kPP3/K1Bb4
    ('6b1/5pp1/6p1/8/8/8/8/8', [], [], 5),  # Willcocks, 5kb1/2pRRp2/3ppKpp/8/8/8/8/8
    ('6b1/5p1p/8/8/8/8/8/8', [], [], 5),  # Same as above
    ('8/8/8/8/8/2P5/1PPP4/8', [], [], 5),  # auxiliary
    ('8/8/8/8/8/8/P1P5/1B6', [], [], 5),  # auxiliary
    ('8/8/8/8/8/1PP5/B1PP4/8', [], [], 5),  # Hoeg, 8/8/8/8/1P6/kP6/2PP4/KBb5
    ('8/8/8/8/1P6/kP6/BrPP4/K7', [], [], 10),  # Same as above
    ('4BN1k/3ppK1p/4p3/8/8/8/8/8', [], [], 5),  # Willcocks, 4BNNk/3ppKR1/4ppp1/8/8/8/8/8
    ('8/8/8/8/8/3P4/P1kPP3/K1nb4', [], [], 5),  # Fabel, 8/8/8/8/8/1P1P4/1PkPP3/K1nb4
    ('4B1rk/3ppKpp/8/8/8/8/8/8', [], [], 5),  # Willcocks, 4BNrk/3ppK1p/6pp/8/8/8/8/8
    ('1K6/1p1pppp1/1pp5/8/8/8/8/8', [], [], 15),  # Keym, k1KB4/PpRpp1p1/b1p2p2/1p6/8/8/8/8
    ('5k1K/3pRpp1/4p3/8/8/8/8/8', [], [], 5),  # Willcocks, 5kbK/3pRp1P/4pp1P/6p1/8/8/8/8
    ('5kbK/3pRp2/4p1p1/8/8/8/8/8', [], [], 5),  # same as above
    ('8/1ppppKp1/6p1/8/8/8/8/8', [], [], 20),  # auxiliary
    ('4B1rr/3ppKpk/7p/8/8/8/8/8', [], [], 5),  # Willcocks, 4BQrr/pp1ppK1k/2p1p1pp/8/8/8/8/8
    ('4Bnrr/1ppppK1k/4p1pp/8/8/8/8/8', [], [], 5),  # same as above
    ('4BQ1q/3ppKpk/7p/8/8/8/8/8', [], [], 5),  # Willcocks, 4BQ1q/3ppK1k/4pp1p/8/8/8/8/8
    ('3Qrb2/ppppp1p1/8/8/8/8/8/8', [], [], 10),  # Mortensen, k1KQRb2/ppppp1p1/5p2/7p/8/8/8/8
    ('1K6/1ppp1pp1/8/8/8/8/8/8', [], [], 10),  # auxiliary
    ('1K1k4/rpppRp2/p3p3/8/8/8/8/8', [], [], 5),  # Keym, RK1k4/r1ppRpp1/pp2p2p/8/8/8/8/8
    ('nK1k4/r1ppRpp1/pp2p3/8/8/8/8/8', [], [], 10),  # same as above
    ('1nRB4/1pKpp3/1pp5/8/8/8/8/8', [], [], 5),  # Willcocks, kBRB4/1pKpp1p1/1pp5/7p/8/8/8/8
    ('3BN1qk/2pRKppp/3p1p2/8/8/8/8/8', [], [], 5),  # Willcocks, 3BN1qk/2pRK1pp/3ppp2/8/8/8/8/8
    ('3B1rqk/2pRKppp/3pp3/8/8/8/8/8', [], [], 5),  # same as above
    ('5K2/1ppp1pp1/8/8/8/8/8/8', [], [], 5),  # auxiliary
    ('2bk1K1n/1ppp1p1q/6pp/8/8/8/8/8', [], [], 5),  # Ceriani, 2bk1K1N/1ppp1p1q/p5pp/8/8/8/8/8

    # Some simple positions to test frozen pieces
    ('8/8/8/8/8/8/6PP/6Nr', ['g1'], [], 5),  # frozen White piece test
    ('5bQ1/5ppp/8/8/8/8/8/8', ['f8'], [], 5)  # frozen Black piece test
]


test_non_cages_data = [
    ('8/8/8/8/8/8/PPPPPPPP/2B1RK2', [], [], 10),  # white kingside castling
    ('8/8/8/8/8/8/PPPPPPPP/KR3B2', [], [], 10),  # white queenside castling
    ('2brk3/pppppppp/8/8/8/8/8/8', [], [], 10),  # black kingside castling
    ('k1r2b2/pppppppp/8/8/8/8/8/8', [], [], 10),  # black queenside castling
    ('8/8/8/8/8/5P2/4PrPP/7K', [], [], 5),  # a blockable check (shouldn't count as a check)
    ('8/8/8/8/8/8/6PP/6Nr', [], [], 5),  # same as frozen White piece test but without frozen pieces
    ('5bQ1/5ppp/8/8/8/8/8/8', [], [], 5)  # same as frozen Black piece test but without frozen pieces
]


class TestCages(unittest.TestCase):
    def test_cages(self):
        print('Testing cages')
        for data in test_cages_data:
            with self.subTest(data=data):
                position, frozen_squares_strings, additional_zone_squares_strings, depth = data
                self.assertEqual(test_position(position,
                                               [get_square(sq) for sq in frozen_squares_strings],
                                               [get_square(sq) for sq in additional_zone_squares_strings],
                                               depth), True)

    def test_non_cages(self):
        print('Testing non cages')
        for data in test_non_cages_data:
            with self.subTest(data=data):
                position, frozen_squares_strings, additional_zone_squares_strings, depth = data
                self.assertEqual(test_position(position,
                                               [get_square(sq) for sq in frozen_squares_strings],
                                               [get_square(sq) for sq in additional_zone_squares_strings],
                                               depth), False)
