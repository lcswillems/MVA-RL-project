import argparse
import datetime
import scipy.stats as stats
from tensorboardX import SummaryWriter
from tqdm import tqdm

from algos import CFR, Exp3P
from games import RockPaperScissors, TicTacToe

parser = argparse.ArgumentParser()
parser.add_argument('--game', required=True,
                    help='game: RPS or TTT')
parser.add_argument('--algo', required=True,
                    help='algorithm: Exp3P or CFR')
parser.add_argument('--iter', type=int, default='100',
                    help='number of policy updates (default: 100)')
parser.add_argument('--eta', type=float, default=0,
                    help='η parameter for Exp3P')
parser.add_argument('--gamma', type=float, default=0,
                    help='γ parameter for Exp3P')
parser.add_argument('--beta', type=float, default=0,
                    help='β parameter for Exp3P')
args = parser.parse_args()

assert args.game in ['RPS', 'TTT']
assert args.algo in ['Exp3P', 'CFR']

if args.algo == 'Exp3P':
    hyper_params = 'η{}_γ{}_β{}'.format(args.eta, args.gamma, args.beta)
elif args.algo == 'CFR':
    hyper_params = ''
date = datetime.datetime.now().strftime("%y%m%d%H%M%S")
writer_path = 'storage/{}_{}_{}_{}'.format(args.game, args.algo, hyper_params, date)
tb_writer = SummaryWriter(writer_path)

if args.game == 'RPS':
    game = RockPaperScissors()
elif args.game == 'TTT':
    game = TicTacToe()

if args.algo == 'Exp3P':
    assert args.game == 'RPS'

    player1 = Exp3P(game.nb_actions, args.eta, args.gamma, args.beta)
    player2 = Exp3P(game.nb_actions, args.eta, args.gamma, args.beta)

    for i in range(args.iter):
        a1 = player1.play()
        a2 = player2.play()
        u = game.utility(a1, a2)
        player1.analyze_feedback(u)
        player2.analyze_feedback(-u)

        tb_writer.add_scalar('u1', u, i)
        tb_writer.add_scalar('H1', stats.entropy(player1.σ), i)
        tb_writer.add_scalar('u2', -u, i)
        tb_writer.add_scalar('H2', stats.entropy(player2.σ), i)

elif args.algo == 'CFR':
    cfr = CFR(game, init_policy="hot")
    for i in tqdm(range(args.iter)):
        print("b{}".format(i), cfr.σ)
        cfr.update_policy()
        print("e{}".format(i), cfr.σ)