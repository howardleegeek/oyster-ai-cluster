## Getting Started

### 1. Environment Setup

Copy the environment template and configure your variables:

```bash
cp env.example .env.local
```

Edit `.env.local` with your configuration:

```bash
# Backend API
NEXT_PUBLIC_BACKEND_BASE_URL=your_backend_url

# App URL
NEXT_PUBLIC_APP_URL=your_app_url


# X (Twitter) Integration: https://docs.x.com/overview
NEXT_PUBLIC_X_CLIENT_ID=your_x_client_id
NEXT_PUBLIC_X_REDIRECT_URI=your_redirect_uri



# Third party RPC service: https://www.helius.dev/, https://www.alchemy.com/
# Solana Configuration
NEXT_PUBLIC_SOLANA_RPC_URL=your_solana_rpc_url
NEXT_PUBLIC_SOLANA_TO_WALLET=your_wallet_address

# Wallet Connect: https://rainbowkit.com/zh-CN/docs/introduction
NEXT_PUBLIC_WAGMI_PROJECT_ID=your_wagmi_project_id

# Social Links
NEXT_PUBLIC_MATRICA_DISCORD_URL=your_discord_url
NEXT_PUBLIC_TELEGRAM_URL=your_telegram_url
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Generate API Types

Generate TypeScript types from the backend API:

```bash
npm run generate-api
```

### 4. Start Development Server

```bash
npm run dev
```

The application will be available at [http://localhost:8081](http://localhost:8081).

## Available Scripts

- `npm run dev` - Start development server on port 8081
- `npm run build` - Build the application for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run generate-api` - Generate API types using Orval

## Development Guidelines

### Environment Variables

- All public environment variables must be prefixed with `NEXT_PUBLIC_`
- Update both `.env.local` and `env.example` when adding new variables
- Never commit actual values to `env.example`

### Code Quality

- Run `npm run lint` before committing
- Follow TypeScript best practices
- Use Prettier for code formatting

### API Integration

- Use the generated API types from `npm run generate-api`
- API configuration is managed through Orval (see `orval.config.js`)

### Wallet Integration

The app supports multiple wallet types:

- Solana wallets (Phantom, Solflare)
- Ethereum wallets via Reown AppKit
- TON Connect for TON wallets

## Testing

### Manual testing (wallet connect / disconnect)

1. **Start the app**: `npm run dev` and open [http://localhost:8081](http://localhost:8081).
2. **Connect wallet**:
   - Click the wallet icon in the header (or “Connect wallet” on the device page).
   - Choose a Solana wallet (e.g. Phantom) and approve the connection.
   - Sign the message when prompted; you should be “authenticated”.
3. **Disconnect wallet** (any of these):
   - **Header**: Click your wallet avatar (first letter) → “Disconnect”.
   - **Profile**: Go to `/profile` → click “Disconnect” under the wallet address.
   - **Device page**: Go to `/device` → in the “Got a Puffy Pass NFT Whitelist?” card, click “Disconnect” (shown when connected).
4. **Verify**: After disconnecting, the header should show the wallet icon again and protected pages (e.g. profile) should redirect to sign-in if required.

### Manual testing (device purchase flow)

1. Go to `/device`.
2. **Wallet**: Connect wallet (see above). Optionally disconnect and reconnect to confirm both work.
3. **Device Pass**: Enter a one-time Device Pass code (if you have one) and click “Apply”; check success/error messages and that the quote updates.
4. **Shipping**: Fill name, country, address, city, postal code, email; leave optional fields as needed.
5. **Order**: Check “I acknowledge…” and click “Pay with USDC” or “Pay with Crypto” (backend must be running and configured for real payments).

### Testing API / hooks without the UI

- **MSW**: The project uses [MSW](https://mswjs.io/) for API mocking (see `src/types/api/**/*.msw.ts`). You can run the app with the mock worker to test flows without a real backend.
- **Hooks**: `useWalletLogin`, `useDevicePurchase`, etc. can be exercised in a small test app or by adding a test framework (e.g. Vitest + React Testing Library) and rendering components that use them.

### Adding automated tests (optional)

To add unit/integration tests:

1. Install Vitest and React Testing Library:
   ```bash
   npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom
   ```
2. Add a `vitest.config.ts` and a `test` script in `package.json` (e.g. `"test": "vitest"`).
3. Write tests for utilities (e.g. in `src/lib`) and for components that use `useWalletLogin` by mocking the wallet and API (e.g. with MSW or Vitest mocks).

## Project Structure

```
src/
├── app/           # Next.js app router pages
├── components/    # Reusable UI components
├── lib/          # Utility functions and configurations
├── hooks/        # Custom React hooks
└── types/        # TypeScript type definitions
```
