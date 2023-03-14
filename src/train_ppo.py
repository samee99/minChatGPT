import click
import torch
from trainers import PPOTrainer
from configs import get_configs
from gpt import GPTActor, GPTRewardModel, GPTCritic
from dataset import DahoasSFTStaticPromptsDataset


def train(batch_size, exp_name):

    cfg = get_configs("gpt2-medium")
    cfg.actor_weights = "./runs/sft_1678085469/original_sft_1678085469_step100000.pt"
    cfg.critic_weights = "./runs/rm_1678145909/rm_1678145909_final.pt"
    cfg.reward_model_weights = "./runs/rm_1678145909/rm_1678145909_final.pt"
    cfg.sft_model_weights = "./runs/sft_1678085469/original_sft_1678085469_step100000.pt"
    cfg.batch_size = batch_size
    cfg.total_epochs = 2
    cfg.exp_name = exp_name

    actor = GPTActor.from_checkpoint(cfg, cfg.actor_weights).cuda()
    critic = GPTCritic.from_checkpoint(cfg, cfg.critic_weights).cuda()
    sft_model = GPTActor.from_checkpoint(cfg, cfg.sft_model_weights).cuda()
    reward_model = GPTRewardModel.from_checkpoint(
        cfg, cfg.reward_model_weights).cuda()

    dataset = DahoasSFTStaticPromptsDataset(block_size=1024,
                                            max_examples=None,
                                            tokenizer_name="tiktoken/gpt2")
    trainer = PPOTrainer(cfg, actor, critic, reward_model, sft_model, dataset)
    trainer.fit()


@click.command()
@click.option('--strategy', '-s')
@click.option('--batch-size', '-b', default=1)
@click.option('--exp-name', '-n', default="default")
def main(strategy, batch_size, exp_name):
    torch.manual_seed(1234)

    train(batch_size, exp_name)


if __name__ == "__main__":
    main()
