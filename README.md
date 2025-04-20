Short Description
A donation contract on Polkadot (via Moonbeam) that securely holds funds and releases them to businesses once a funding goal is met.

Full Description
Project Overview
We’re building a fully-functional decentralized donation platform that allows donors to transparently fund charity-led projects and automatically allocate payments to verified companies contributing services or goods. The platform is built using Flask for the frontend and backend, with SQLAlchemy for database management and a custom Polkadot-based smart contract system that handles payment distribution.

Problem Statement
In traditional charity systems, there’s a lack of transparency in how donations are spent. Donors are often unaware of where their money goes after it leaves their wallets, and charities struggle to provide real-time accountability, especially when projects involve third-party contractors or suppliers. This creates mistrust and inefficiency, discouraging potential donors and limiting long-term impact.

Solution
Our dApp allows charities to list projects and define the suppliers or companies involved in delivering each part of the initiative. For each project, the charity allocates a percentage of the total budget to each participating company. When a donor funds the project, their contribution is automatically split among the stakeholders via a Polkadot smart contract—ensuring every participant gets paid only according to the agreed terms.

The donor can see exactly where their money went, how much was allocated to each company, and how much has been raised in total. Companies can onboard using wallet addresses, and all smart contracts are deployed at project creation using the donor-provided private key—adding another layer of decentralization and autonomy.

What We’ve Built
We’ve built a complete multi-role system using Flask with login and registration for donors, companies, and charities. Charities can create and manage projects, assigning percentages and wallet addresses to companies. Donors can view all active projects, donate directly through the platform, and track how their funds are split and used.

Donations trigger a smart contract on the Polkadot network (deployed via deploy_proposal()), which splits the funds based on pre-set allocations and sends them to respective wallet addresses. All transactions are logged, and donation history is available per user, showing which projects they supported and how their money was distributed.

Technical Architecture
The backend is built with Flask, Flask-Login, and SQLAlchemy. The donation logic and smart contract deployment are handled via a custom SDK that interfaces with the Polkadot blockchain. We’ve used Substrate’s contract pallet to deploy WebAssembly-based smart contracts directly from our backend using minimal wrapper functions. All contract logic is written to mirror the business logic of budget splits and enforce strict payouts.

Why Polkadot
Polkadot’s cross-chain architecture and low-latency transaction processing made it an ideal foundation. The Substrate SDK allowed us to deploy project-specific smart contracts that enforce budget rules without requiring a centralized payment processor. The platform’s flexibility, plus the ability to interact with parachains in the future, opens the door for verifying supplier credentials, auditing wallets, or attaching proof-of-impact oracles.

Impact
This project reduces donor hesitation by providing total transparency and automating the hardest part of donation logistics—trust. Charities gain credibility, companies gain accountability, and donors gain confidence. It’s a smart contract-powered model of trust-by-design for social good, directly enabled by Polkadot.

Next Steps
We’re seeking a grant to further productionize the smart contract interface, develop a user-friendly Polkadot wallet plugin for donors, and add advanced features like milestone-based vesting, supplier verification, and real-time impact metrics. With funding, we can expand testing, audit our contracts, and launch publicly with a handful of live charity pilots.

Technical Explanation

This project was built as a full-stack decentralized application (dApp) that bridges traditional web infrastructure with Polkadot’s smart contract capabilities to ensure transparency, trust, and automated fund allocation for charity projects. The architecture is modular, with clearly separated concerns between the user interface, the backend logic, and the on-chain components.

Frontend and Backend Stack

The user interface is built using Python Flask for both the frontend templating and backend routing. Flask-Login handles authentication across three distinct user roles: donors, charities, and suppliers (companies). Each user role has access to a tailored dashboard, powered by Jinja2 templates, and dynamic rendering based on role-specific permissions.

The backend uses SQLAlchemy to manage relational data models for users, projects, donations, and payment splits. This relational schema lets us enforce clean boundaries between donors and recipients, and it supports multi-project, multi-user scaling.

All blockchain interactions are abstracted into a separate module using PySubstrateInterface, which communicates with a local or remote Substrate node. This modular design enables easy swapping of the backend chain (to other parachains or testnets) and provides robust separation between off-chain and on-chain logic.

Smart Contract Layer

The core of the innovation lies in our use of Polkadot’s Substrate Contracts pallet, which allows for WebAssembly-based smart contracts using the ink! programming language. Each project created by a charity dynamically triggers a contract deployment that encodes the donation split logic. Here’s how it works:

When a charity creates a project, the Flask backend triggers deploy_proposal()—a function that compiles and deploys a new ink! smart contract on a chosen Substrate chain (like Rococo or a local dev chain).

The contract includes:

A list of wallet addresses (company recipients).

The percentage of total donations assigned to each recipient.

Functions to accept a donation and automatically distribute funds based on the stored allocation table.

Once a donor contributes, the funds are received by the contract and immediately split and transferred to the respective company wallets using the pay() function.

Why Polkadot?

Polkadot was chosen for several reasons:

Smart Contracts with Strong Guarantees: The Contracts pallet enables deterministic execution with sandboxing and low-latency deployment of WASM-based smart contracts. Unlike Solidity/EVM environments, ink! contracts offer finer-grained control over gas metering and execution weight, giving us confidence in cost predictability and runtime safety.

Modular Runtime and Parachain Potential: Because of Substrate's pluggable architecture, this project could eventually evolve into a dedicated parachain or leverage parathreads. That means we could bake in features like zero-knowledge proof verification of supplier credibility or milestone-triggered vesting natively into runtime logic instead of smart contracts alone.

Developer Ecosystem: Tools like Canvas UI and Polkadot-JS make contract interaction during development and testing very smooth. We used Contracts UI for initial debugging and contract state monitoring. Substrate’s RPC endpoints also allowed our Flask app to easily query on-chain state and show users live balances and donation history.

Low Fees and High Performance: Compared to Ethereum, Polkadot’s fee model allowed us to build a system where multiple micro-transactions (e.g., $5–$10 donations) wouldn’t be eaten alive by gas costs. This is critical for donors who want transparency without extra overhead.

Decentralization by Design: We allow contracts to be deployed from the donor’s own wallet, not the backend, meaning the trust model doesn't rely on our servers. The donor provides their private key (locally via browser plugin or hardware wallet integration in future versions), and the contract is created in a trustless way—directly reflecting their funding action.

Future Extensions Using Polkadot

Polkadot’s cross-chain architecture opens the door for some ambitious upgrades:

Integrate on-chain identity via Polkadot’s DID module to verify company legitimacy.

Use XCMP to bridge donation verification to other parachains that handle auditing or reputation scoring.

Implement milestone-based release with oracle support for real-world event confirmation (e.g., supplier delivery receipts).

Leverage ZK-based proofs or off-chain workers to check real-time charity progress and reflect it in contract state.


VIDEO LINK
https://youtu.be/9h3qZqezH3o
