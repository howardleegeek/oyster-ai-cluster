"""Run this test to create test data in the REAL database (from .env settings)."""

import pytest
from app.models.user import User, Balance, PromoteNft
from app.models.product import Campaign, Product
from app.enums import Chain, VmType, ProductType
from decimal import Decimal
import datetime


def test_create_real_test_data(real_db_session):
    """
    This test creates comprehensive test data in the REAL database.
    Run with: pytest tests/create_real_test_data.py -v -s

    WARNING: This writes to your actual database configured in .env

    Creates:
    - 3 users with balances
    - 2 campaigns
    - 4 products
    - 3 promote nfts (user1: 0, user2: 1, user3: 2)
    """
    print("\n=== Creating Test Data in REAL Database ===")

    # ============================================================================
    # Create 2 Campaigns
    # ============================================================================
    campaign1 = Campaign(
        id=1001,
        name="Puffy Campaign",
        edition="v1",
        requirement="Hold Puffy NFT",
        collection_address="EQPuffyCollectionAddress",
        collection_name="Puffy Collection",
        chain=Chain.TON,
        vm_type=VmType.TVM
    )
    real_db_session.add(campaign1)

    campaign2 = Campaign(
        id=1002,
        name="Soon Campaign",
        edition="v1",
        requirement="Hold Soon NFT",
        collection_address="EQSoonCollectionAddress",
        collection_name="Soon Collection",
        chain=Chain.TON,
        vm_type=VmType.TVM
    )
    real_db_session.add(campaign2)
    print(f"\n✓ Campaigns created: ID {campaign1.id} ({campaign1.name}), ID {campaign2.id} ({campaign2.name})")

    # ============================================================================
    # Create 3 Users with Balances
    # ============================================================================
    users = []
    user_data = [
        ("user_001", "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU", 50),
        ("user_002", "EQAnotherUserAddress123456789abcdefghijk", 100),
        ("user_003", "EQThirdUserAddress987654321zyxwvutsrq", 150),
    ]

    for user_id, address, points in user_data:
        user = User(
            id=user_id,
            address=address,
            address_hex=f"0x{address}",
            twitter=None,
            email=None,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        real_db_session.add(user)

        balance = Balance(
            id=user_id,
            referrals=0,
            indirect_referrals=0,
            points=points,
            usd=Decimal("0.00"),
            total_usd=Decimal("0.00"),
            updated_at=datetime.datetime.now()
        )
        real_db_session.add(balance)
        users.append(user)
    print(f"\n✓ Users created: {[u.id for u in users]}")

    # ============================================================================
    # Create 4 Products
    # ============================================================================
    products = []
    product_data = [
        ("prod_001", "Phantom Vape", "Premium phantom vape device", ProductType.VAPE, Decimal("49.99")),
        ("prod_002", "Fresh Mint", "Refreshing mint flavor", ProductType.FRESH, Decimal("19.99")),
        ("prod_003", "Puffy Merch", "Official puffy merchandise", ProductType.OTHER, Decimal("29.99")),
        ("prod_004", "Starter Kit", "Complete starter kit", ProductType.OTHER, Decimal("79.99")),
    ]

    for prod_id, name, desc, ptype, price in product_data:
        product = Product(
            id=prod_id,
            name=name,
            description=desc,
            price=price,
            qty=100,
            product_type=ptype,
            passcode_enabled=False,
            sm_icon_url=None,
            md_icon_url=None,
            lg_icon_url=None,
            image_url=None,
            reward_points=10,
            reward_referee_points=5
        )
        real_db_session.add(product)
        products.append(product)
    print(f"\n✓ Products created: {[p.id for p in products]}")

    # ============================================================================
    # Create PromoteNfts
    # user_001: 0 promote nfts
    # user_002: 1 promote nft (belongs to campaign1)
    # user_003: 2 promote nfts (1 belongs to campaign1, 1 belongs to campaign2)
    # ============================================================================
    promote_nfts = []

    # user_002 gets 1 NFT from campaign1
    promote_nft1 = PromoteNft(
        id=1,
        user_id="user_002",
        nft_address="EQNft1User002Campaign1",
        campaign_id=campaign1.id
    )
    real_db_session.add(promote_nft1)
    promote_nfts.append(promote_nft1)

    # user_003 gets 2 NFTs (1 from each campaign)
    promote_nft2 = PromoteNft(
        id=2,
        user_id="user_003",
        nft_address="EQNft2User003Campaign1",
        campaign_id=campaign1.id
    )
    real_db_session.add(promote_nft2)
    promote_nfts.append(promote_nft2)

    promote_nft3 = PromoteNft(
        id=3,
        user_id="user_003",
        nft_address="EQNft3User003Campaign2",
        campaign_id=campaign2.id
    )
    real_db_session.add(promote_nft3)
    promote_nfts.append(promote_nft3)

    print(f"\n✓ PromoteNfts created:")
    print(f"  - user_001: 0 NFTs")
    print(f"  - user_002: 1 NFT (campaign_id={campaign1.id})")
    print(f"  - user_003: 2 NFTs (campaign_ids={campaign1.id}, {campaign2.id})")

    # Commit all changes
    real_db_session.commit()

    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(f"Users: {len(users)} (user_001, user_002, user_003)")
    print(f"Campaigns: {2} (IDs: {campaign1.id}, {campaign2.id})")
    print(f"Products: {len(products)} (prod_001, prod_002, prod_003, prod_004)")
    print(f"PromoteNfts: {len(promote_nfts)} (user_001: 0, user_002: 1, user_003: 2)")
    print("="*60)
    print("\n✅ Data Committed to Database")

    # Note: rollback won't happen here since we explicitly committed
    assert True
