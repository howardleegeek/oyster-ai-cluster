"""Run this test to create test data in the database."""

def test_create_test_data(test_user_with_balance, test_campaign, test_product, test_promote_nft):
    """
    This test creates test data in the database.
    Run with: pytest tests/create_test_data.py -v -s
    """
    print("\n=== Test Data Created ===")
    print(f"User ID: {test_user_with_balance.id}")
    print(f"User Address: {test_user_with_balance.address}")
    print(f"Balance Points: {test_user_with_balance.balance.points}")

    print(f"\nCampaign ID: {test_campaign.id}")
    print(f"Campaign Name: {test_campaign.name}")
    print(f"Campaign Chain: {test_campaign.chain}")

    print(f"\nProduct ID: {test_product.id}")
    print(f"Product Name: {test_product.name}")
    print(f"Product Price: {test_product.price}")

    print(f"\nPromoteNft ID: {test_promote_nft.id}")
    print(f"PromoteNft User ID: {test_promote_nft.user_id}")
    print(f"PromoteNft Campaign ID: {test_promote_nft.campaign_id}")
    print(f"PromoteNft NFT Address: {test_promote_nft.nft_address}")

    # Data is committed to database by the fixtures
    assert True
