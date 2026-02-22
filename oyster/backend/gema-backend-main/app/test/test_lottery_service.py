from decimal import Decimal
from typing import Tuple, Dict

from app.db.base import SessionLocal
from app.db.lottery import Lottery as LotteryRepo
from app.models.product import Product
from app.models.lottery import LotteryStrategy, LotteryProbability
from app.schemas.lottery import (
    LotteryStrategyCreate,
    LotteryProbabilityCreate,
)
from app.services.lottery import LotteryService


def format_statistics(counts: Dict[int, int], total_runs: int, strategy_name: str):
    """
    Format statistics output in a readable table format.
    
    Args:
        counts: Dictionary mapping product_id to count
        total_runs: Total number of runs
        strategy_name: Name of the strategy for display
    """
    print(f"\n{'='*60}")
    print(f"Strategy: {strategy_name} (Total runs: {total_runs})")
    print(f"{'='*60}")
    print(f"{'Product ID':<12} {'Count':<10} {'Percentage':<12} {'Expected %':<12}")
    print(f"{'-'*60}")
    
    # Sort by product_id for consistent output
    sorted_items = sorted(counts.items())
    for product_id, count in sorted_items:
        percentage = (count / total_runs) * 100
        print(f"{product_id:<12} {count:<10} {percentage:>10.2f}% {'':<12}")
    
    print(f"{'='*60}\n")


def format_tree_statistics(counts: Dict[int, int], total_runs: int, products: list):
    """
    Format tree strategy statistics grouped by child strategy.
    
    Args:
        counts: Dictionary mapping product_id to count
        total_runs: Total number of runs
        products: List of products (index 0-8 correspond to products 1-9)
    """
    print(f"\n{'='*70}")
    print(f"Strategy: Tree Strategy (Total runs: {total_runs})")
    print(f"{'='*70}")
    
    # Group products by child strategy
    child_1_products = products[0:3]  # products 1,2,3
    child_2_products = products[3:6]   # products 4,5,6
    child_3_products = products[6:9]   # products 7,8,9
    
    child_groups = [
        ("Child Strategy 1 (Expected: ~10% each)", child_1_products, 10.0),
        ("Child Strategy 2 (Expected: ~20% each)", child_2_products, 20.0),
        ("Child Strategy 3 (Expected: ~30% each)", child_3_products, 30.0),
    ]
    
    for group_name, group_products, expected_pct in child_groups:
        print(f"\n{group_name}:")
        print(f"{'Product ID':<12} {'Count':<10} {'Percentage':<12} {'Expected %':<12}")
        print(f"{'-'*50}")
        
        group_total = 0
        for product in group_products:
            count = counts.get(product.id, 0)
            group_total += count
            percentage = (count / total_runs) * 100
            print(f"{product.id:<12} {count:<10} {percentage:>10.2f}% {expected_pct:>10.2f}%")
        
        group_pct = (group_total / total_runs) * 100
        print(f"{'Group Total':<12} {group_total:<10} {group_pct:>10.2f}% {expected_pct*3:>10.2f}%")
    
    print(f"\n{'='*70}\n")

# source ~/venv/bin/activate
# python3 -m app.test.test_lottery_service
def setup_mock_data(db) -> Tuple[LotteryService, int, int, int]:
    """
    Prepare mock data in the real test database for lottery service testing.

    This function will:
    1. Create nine test products
    2. Create three kinds of lottery strategies:
       - Equal strategy: 50% / 50% probability for first two products
       - Weighted strategy: probability based on product index (10%, 20%, ..., 90%)
       - Tree strategy: one root strategy with three child strategies (3x3 products)
         * root -> child_1, child_2, child_3
         * child_1 -> products 1, 2, 3
         * child_2 -> products 4, 5, 6
         * child_3 -> products 7, 8, 9
    3. Create corresponding probability records for each strategy

    Returns:
        (lottery_service, equal_strategy_id, weighted_strategy_id, tree_root_strategy_id)
    """
    # Optional: clean previous test data to avoid growing the table indefinitely
    # Delete in correct order to respect foreign key constraints:
    # 1. Delete lottery_probabilities (references products and strategies)
    # 2. Delete lottery_strategies (may reference other strategies via next_strategy_id)
    # 3. Delete products
    
    # Find test products first
    test_products = db.query(Product).filter(Product.name.like("Test Product %")).all()
    test_product_ids = [p.id for p in test_products]
    
    if test_product_ids:
        # Find test strategies (by name pattern)
        test_strategies = db.query(LotteryStrategy).filter(
            LotteryStrategy.name.like("test_strategy%")
        ).all()
        test_strategy_ids = [s.id for s in test_strategies]
        
        if test_strategy_ids:
            # Delete all probabilities that reference test strategies or test products
            db.query(LotteryProbability).filter(
                (LotteryProbability.strategy_id.in_(test_strategy_ids)) |
                (LotteryProbability.next_strategy_id.in_(test_strategy_ids)) |
                (LotteryProbability.product_id.in_(test_product_ids))
            ).delete(synchronize_session=False)
            db.commit()
            
            # Delete test strategies
            db.query(LotteryStrategy).filter(
                LotteryStrategy.id.in_(test_strategy_ids)
            ).delete(synchronize_session=False)
            db.commit()
        
        # Delete test products
        db.query(Product).filter(Product.id.in_(test_product_ids)).delete(synchronize_session=False)
        db.commit()

    # Create test products
    products = []
    for i in range(1, 10):
        # Create 9 simple test products with different prices and quantities
        p = Product(
            name=f"Test Product {i}",
            description=f"Test product {i} for lottery",
            price=Decimal(f"{i * 10}.00"),
            qty=100 + i,
            sm_icon_url=None,
            md_icon_url=None,
            lg_icon_url=None,
            image_url=None,
            reward_points=10 * i,
            reward_referee_points=5 * i,
        )
        products.append(p)

    db.add_all(products)
    db.commit()
    for p in products:
        db.refresh(p)

    # Create lottery service and strategies
    repo = LotteryRepo(db)
    service = LotteryService(repo)

    # Strategy 1: equal distribution (50% / 50% for first two products)
    equal_strategy = service.create_strategy(
        LotteryStrategyCreate(
            name="test_strategy_equal",
            description="Strategy with equal probability for first two products",
        )
    )

    # Create probability records (50% / 50% for two products)
    prob1 = service.create_probability(
        LotteryProbabilityCreate(
            strategy_id=equal_strategy.id,
            product_id=products[0].id,
            probability=500,
        )
    )
    prob2 = service.create_probability(
        LotteryProbabilityCreate(
            strategy_id=equal_strategy.id,
            product_id=products[1].id,
            probability=500,
        )
    )

    # Strategy 2: weighted distribution based on product index
    weighted_strategy = service.create_strategy(
        LotteryStrategyCreate(
            name="test_strategy_weighted",
            description="Strategy with weighted probability based on product index",
        )
    )

    # For simplicity, use index 1..9 as weight factor, probability = index * 10 (10, 20, ..., 90)
    # Note: The sum does not have to be 1000; relative weights are what matter.
    weighted_probs = []
    for idx, product in enumerate(products, start=1):
        prob = service.create_probability(
            LotteryProbabilityCreate(
                strategy_id=weighted_strategy.id,
                product_id=product.id,
                probability=idx * 10,
            )
        )
        weighted_probs.append(prob)

    # Strategy 3: two-level tree (root -> three child strategies -> products)
    # Root strategy can draw child strategies 1, 2, 3 with different probabilities (10%, 20%, 30%)
    tree_root_strategy = service.create_strategy(
        LotteryStrategyCreate(
            name="test_strategy_tree_root",
            description="Root strategy for 3x3 tree",
        )
    )

    child_1 = service.create_strategy(
        LotteryStrategyCreate(
            name="test_strategy_tree_child_1",
            description="Child strategy 1 (products 1,2,3)",
        )
    )
    child_2 = service.create_strategy(
        LotteryStrategyCreate(
            name="test_strategy_tree_child_2",
            description="Child strategy 2 (products 4,5,6)",
        )
    )
    child_3 = service.create_strategy(
        LotteryStrategyCreate(
            name="test_strategy_tree_child_3",
            description="Child strategy 3 (products 7,8,9)",
        )
    )

    # Root probabilities: child_1:10%, child_2:20%, child_3:30% (relative weights: 100, 200, 300)
    tree_root_probs = []
    root_weights = {
        child_1.id: 100,
        child_2.id: 200,
        child_3.id: 300,
    }
    for child_strategy in [child_1, child_2, child_3]:
        prob = service.create_probability(
            LotteryProbabilityCreate(
                strategy_id=tree_root_strategy.id,
                next_strategy_id=child_strategy.id,
                probability=root_weights[child_strategy.id],
            )
        )
        tree_root_probs.append(prob)

    # Child 1: products 1,2,3
    tree_child_1_probs = []
    for product in products[0:3]:
        prob = service.create_probability(
            LotteryProbabilityCreate(
                strategy_id=child_1.id,
                product_id=product.id,
                probability=333,
            )
        )
        tree_child_1_probs.append(prob)

    # Child 2: products 4,5,6
    tree_child_2_probs = []
    for product in products[3:6]:
        prob = service.create_probability(
            LotteryProbabilityCreate(
                strategy_id=child_2.id,
                product_id=product.id,
                probability=333,
            )
        )
        tree_child_2_probs.append(prob)

    # Child 3: products 7,8,9
    tree_child_3_probs = []
    for product in products[6:9]:
        prob = service.create_probability(
            LotteryProbabilityCreate(
                strategy_id=child_3.id,
                product_id=product.id,
                probability=333,
            )
        )
        tree_child_3_probs.append(prob)

    print("Created equal strategy:", equal_strategy)
    print("Created equal probabilities:", prob1, prob2)
    print("Created weighted strategy:", weighted_strategy)
    print("Created weighted probabilities:", weighted_probs)
    print("Created tree root strategy:", tree_root_strategy)
    print("Created tree child strategies:", child_1, child_2, child_3)
    print("Created tree root probabilities:", tree_root_probs)
    print("Created tree child_1 probabilities:", tree_child_1_probs)
    print("Created tree child_2 probabilities:", tree_child_2_probs)
    print("Created tree child_3 probabilities:", tree_child_3_probs)

    return service, equal_strategy.id, weighted_strategy.id, tree_root_strategy.id, products


def run_lottery_tests():
    """
    Entry point for manual testing of LotteryService with real database.
    """
    db = SessionLocal()
    try:
        service, equal_strategy_id, weighted_strategy_id, tree_root_strategy_id, products = setup_mock_data(db)

        # Test draw_award for equal strategy (run 1000 times and collect stats)
        print("\n" + "="*60)
        print("Testing draw_award (equal strategy, 1000 runs)")
        print("="*60)
        equal_counts = {}
        for i in range(1000):
            product_id = service.draw_award(equal_strategy_id)
            equal_counts[product_id] = equal_counts.get(product_id, 0) + 1
        format_statistics(equal_counts, 1000, "Equal Strategy (Expected: 50% / 50%)")

        # Test draw_award for weighted strategy (run 1000 times and collect stats)
        print("\n" + "="*60)
        print("Testing draw_award (weighted strategy, 1000 runs)")
        print("="*60)
        weighted_counts = {}
        for i in range(1000):
            product_id = service.draw_award(weighted_strategy_id)
            weighted_counts[product_id] = weighted_counts.get(product_id, 0) + 1
        format_statistics(weighted_counts, 1000, "Weighted Strategy (Expected: increasing with product index)")

        # Test tree strategy (root -> child strategies -> products) with 1000 runs
        print("\n" + "="*60)
        print("Testing draw_award (tree strategy, 1000 runs)")
        print("="*60)
        tree_counts = {}
        for i in range(1000):
            product_id = service.draw_award(tree_root_strategy_id)
            tree_counts[product_id] = tree_counts.get(product_id, 0) + 1
        format_tree_statistics(tree_counts, 1000, products)

        # Test probability tree with limited depth for equal strategy
        print("\n" + "="*60)
        print("Testing get_probability_tree_by_strategy (equal, depth=1)")
        print("="*60)
        tree_depth_1 = service.get_probability_tree_by_strategy(equal_strategy_id, depth=1)
        print(tree_depth_1.model_dump_json(indent=2))

        print("\n" + "="*60)
        print("Testing get_probability_tree_by_strategy (equal, no depth limit)")
        print("="*60)
        tree_full = service.get_probability_tree_by_strategy(equal_strategy_id)
        print(tree_full.model_dump_json(indent=2))

        print("\n" + "="*60)
        print("Testing get_probability_tree_by_strategy (tree, no depth limit)")
        print("="*60)
        tree_root = service.get_probability_tree_by_strategy(tree_root_strategy_id)
        print(tree_root.model_dump_json(indent=2))

    finally:
        db.close()


if __name__ == "__main__":
    run_lottery_tests()
