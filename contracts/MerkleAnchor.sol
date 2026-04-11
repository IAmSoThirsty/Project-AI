// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title MerkleAnchor
 * @dev Smart contract for anchoring Merkle roots to blockchain for constitutional sovereignty
 * 
 * This contract provides immutable, blockchain-backed proof of Merkle root anchoring
 * for the Sovereign Governance Substrate audit log system. Each Merkle root is stored
 * with its Genesis ID and metadata, creating an immutable record that survives:
 * - VM snapshot rollback (VECTOR 3)
 * - Filesystem wipe and restoration (VECTOR 11)
 * - Key compromise with historical rewrite (VECTOR 10)
 * 
 * Architecture:
 *   - Merkle roots are stored in a nested mapping: merkleRoot => genesisId => Anchor
 *   - Each anchor includes timestamp (from block.timestamp) and metadata JSON
 *   - Anchors are write-once (cannot be modified once created)
 *   - Events are emitted for off-chain indexing and verification
 * 
 * Gas Optimization:
 *   - Uses bytes32 for merkle roots (most efficient storage)
 *   - Metadata stored as string (JSON) for flexibility
 *   - Single transaction for anchor creation
 * 
 * Security:
 *   - No owner/admin (fully decentralized)
 *   - Write-once semantics (prevents tampering)
 *   - Public verification (anyone can verify anchors)
 */
contract MerkleAnchor {
    // Anchor record structure
    struct Anchor {
        uint256 timestamp;  // Block timestamp when anchored
        string metadata;    // JSON metadata (batch info, anchor ID, etc.)
        bool exists;        // Existence flag
    }
    
    // Nested mapping: merkleRoot => genesisId => Anchor
    mapping(bytes32 => mapping(string => Anchor)) public anchors;
    
    // Event emitted when a Merkle root is anchored
    event MerkleRootAnchored(
        bytes32 indexed merkleRoot,
        string indexed genesisId,
        uint256 timestamp,
        string metadata
    );
    
    /**
     * @dev Anchor a Merkle root to the blockchain
     * @param merkleRoot The Merkle root hash (bytes32)
     * @param genesisId The Genesis ID for identity binding
     * @param metadata JSON metadata (batch size, timestamp, anchor ID, etc.)
     * 
     * Requirements:
     * - The anchor must not already exist (write-once)
     * 
     * Emits:
     * - MerkleRootAnchored event
     */
    function anchorMerkleRoot(
        bytes32 merkleRoot,
        string memory genesisId,
        string memory metadata
    ) public {
        require(!anchors[merkleRoot][genesisId].exists, "Anchor already exists");
        
        anchors[merkleRoot][genesisId] = Anchor({
            timestamp: block.timestamp,
            metadata: metadata,
            exists: true
        });
        
        emit MerkleRootAnchored(merkleRoot, genesisId, block.timestamp, metadata);
    }
    
    /**
     * @dev Verify if a Merkle root anchor exists
     * @param merkleRoot The Merkle root hash to verify
     * @param genesisId The Genesis ID to verify
     * @return exists True if the anchor exists
     * @return timestamp The block timestamp when anchored (0 if not exists)
     * @return metadata The anchor metadata (empty if not exists)
     */
    function verifyAnchor(
        bytes32 merkleRoot,
        string memory genesisId
    ) public view returns (bool exists, uint256 timestamp, string memory metadata) {
        Anchor memory anchor = anchors[merkleRoot][genesisId];
        return (anchor.exists, anchor.timestamp, anchor.metadata);
    }
}
