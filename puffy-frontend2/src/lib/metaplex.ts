import { mplCandyMachine } from "@metaplex-foundation/mpl-core-candy-machine";
import {
  generateSigner,
  publicKey,
  Umi,
  UmiPlugin,
} from "@metaplex-foundation/umi";
import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import {
  createProgrammableNft,
  fetchAllDigitalAssetWithTokenByOwner,
} from "@metaplex-foundation/mpl-token-metadata";
import { percentAmount } from "@metaplex-foundation/umi";
import { mplCore } from "@metaplex-foundation/mpl-core";
import { Connection } from "@solana/web3.js";

const findNftInWallet = async (
  umi: Umi,
  walletPublicKey: string,
  collectionId: string
) => {
  // Convert wallet public key to UMI public key
  const ownerPublicKey = publicKey(walletPublicKey);

  try {
    // Fetch all NFTs owned by the wallet
    const allNFTs = await fetchAllDigitalAssetWithTokenByOwner(
      umi,
      ownerPublicKey
    );
    console.log("allNFTs", allNFTs);

    // Filter NFTs by collection ID (symbol)
    const collectionNft = allNFTs.find(
      // @ts-expect-error: collection is Option<Collection>
      (nft) => nft?.metadata?.collection?.value?.key === collectionId
    );
    console.log("collectionNft", collectionNft);

    return {
      hasNFT: !!collectionNft,
      mintAddress: collectionNft?.publicKey || null,
    };
  } catch (error) {
    console.error("Error fetching NFTs:", error);
    return {
      hasNFT: false,
      mintAddress: null,
    };
  }
};

export const mintSVMpNFT = async ({
  identity,
  network,
  name,
  symbol,
  uri,
  collectionId,
}: {
  identity: UmiPlugin;
  network: "soon" | "sol";
  name: string;
  symbol: string;
  uri: string;
  collectionId: string;
}) => {
  // create umi
  let umi: Umi | null = null;
  if (network === "soon") {
    umi = createUmi(process.env.NEXT_PUBLIC_SOON_RPC_URL as string)
      .use(mplCore())
      .use(mplCandyMachine());
  } else if (network === "sol") {
    const connection: Connection = new Connection(
      process.env.NEXT_PUBLIC_SOLANA_RPC_URL as string,
      { commitment: "confirmed" }
    );
    umi = createUmi(connection).use(mplCore()).use(mplCandyMachine());
  }
  if (!umi) throw new Error("Umi not initialized");
  // set the identity to the umi
  umi.use(identity);

  // check if wallet has NFT
  // if it does, return the minted address directly and skip the minting process
  // to avoid the NFT being created twice
  const data = await findNftInWallet(umi, umi.identity.publicKey, collectionId);

  if (data.hasNFT) {
    return data.mintAddress;
  }

  const collectionMint = generateSigner(umi);
  const collection = {
    verified: false,
    key: publicKey(collectionId),
  };

  await createProgrammableNft(umi, {
    mint: collectionMint,
    name,
    symbol,
    uri,
    sellerFeeBasisPoints: percentAmount(5.5), // 5.5%
    isMutable: true,
    tokenOwner: umi.identity.publicKey,
    collection,
  }).sendAndConfirm(umi);

  console.log("minting params", {
    mint: collectionMint.publicKey,
    name,
    symbol,
    uri,
    collectionId,
    umi: umi.identity.publicKey,
  });
  return collectionMint.publicKey;
};
