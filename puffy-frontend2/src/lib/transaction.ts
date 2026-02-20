import { createMemoInstruction } from '@solana/spl-memo';
import {
  PublicKey,
  Transaction,
  SystemProgram,
  LAMPORTS_PER_SOL,
  Connection,
} from '@solana/web3.js';

export const buildConnection = () => {
  return new Connection(process.env.NEXT_PUBLIC_SOLANA_RPC_URL as string, { commitment: "confirmed" });
}

export const sendAndConfirmTransaction = async (
  transaction: Transaction,
  sendTransaction: (transaction: Transaction) => Promise<string>,
  confirmTransaction: (signature: string) => Promise<void>,
) => {
  let signature = "";
  try {
    signature = await sendTransaction(transaction);
  } catch (error) {
    throw error;
  }
  try {
    await confirmTransaction(signature);
  } catch (error) {
    throw error;
  }
  return signature;
}

export const buildNftMintingTransaction = async (publicKey: PublicKey, nftId: number, userId: string, gas: number) => {
  const connection = buildConnection();
  const memo = JSON.stringify({
    nft_id: nftId,
    user_id: userId,
  });

  const transaction = new Transaction()
    .add(
      SystemProgram.transfer({
        fromPubkey: publicKey,
        toPubkey: new PublicKey(process.env.NEXT_PUBLIC_SOLANA_TO_WALLET as string),
        lamports: gas * LAMPORTS_PER_SOL,
      }),
    )
    .add(createMemoInstruction(memo, [new PublicKey(publicKey)]));

  const latestBlockhash = await connection.getLatestBlockhash();
  transaction.recentBlockhash = latestBlockhash.blockhash;
  transaction.lastValidBlockHeight = latestBlockhash.lastValidBlockHeight;
  transaction.feePayer = new PublicKey(publicKey);

  return transaction;
}