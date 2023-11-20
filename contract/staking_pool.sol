pragma solidity ^0.8.0;

interface GoerliDeposit {
    function deposit(
        bytes calldata pubkey,
        bytes calldata withdrawal_credentials,
        bytes calldata signature,
        bytes32 deposit_data_root
    ) external payable;
}


// 取款合约逻辑
contract WithdrawalCredential {

    address public owner;

    address payable[4]  stakers;

    constructor(address initialOwner, address payable[4] memory initialStakers) {
        owner = initialOwner; // 合约创建者成为合约的所有者
        stakers = initialStakers;
    }

    // modifier onlyOwner() {
    //     require(msg.sender == owner, "Only the owner can call this function");
    //     _; // 这里的 _ 表示修饰器内部的代码和被修饰函数的代码之间的分隔符
    // }


    function fund(uint256[] memory balanceInfo) external payable {
        // TODO : 访问控制
        
        for (uint i = 0; i < stakers.length; i++) 
        {
            uint256 amount = balanceInfo[i] * 10 ** 15;
            stakers[i].transfer(amount);
        }  
    }    

    function fundExit(uint256 listIdx) external payable {
        // TODO : 访问控制
        
        uint256 amount = 1 * 10 ** 15;
        stakers[listIdx].transfer(amount);
    
    }    

    receive() external payable {
        // 在这里处理接收到的以太币
    }
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//// 合约
contract StakingPool{

    // 预备存款合约
    GoerliDeposit internal  goerliDeposit; // GoerliDeposit 的接口
    constructor() {
        goerliDeposit = GoerliDeposit(0xff50ed3d0ec03aC01D4C79aAd74928BFF48a7b2b); // 初始化 GoerliDeposit 的接口
    }


    ////////////////////////////////////////////////////////////////////////////////////////////////
    //// struct
    struct Cluster {
        uint256 clusterIndex;             // 从1开始
        uint256 clusterSize;
        uint256 clusterNodesAmount;
        uint256[] nodePublicKeyXs;        // 只存公钥横坐标

        //DKG info : 对应于node中 DKG info

        // 按照注册顺序存储
        bytes32[]  shareDistributionHashes;         // encry
        uint256[2][]  commitments1stCoefficients;           
        uint256[2][]  keyShares;
        uint256[4] masterPublicKey;

        //required deposit information
        address withdrawalCredential;   
        bytes[] validatorPublicKey;       //bls12的公钥,48字节
        bytes[] signature;                //96字节
        bytes32[] depositDataRoot;

        //exit
        uint laggingTrigExit;
    }


    struct Node{
        uint256 nodeIndex;                //从1开始
        address nodeAddress;     
        uint256 clusterIndex;
        uint256 clusterSize;   

        // DKG info
        uint256[2] nodePublicKey;         //bn128, 公钥由横纵坐标组成; 用于加密polynomial share
        bytes32 shareDistributionHash;
        uint256[2] commitments1stCoefficient;
        uint256[2] keyShare;
        uint256[4] masterPublicKey;
        uint256[2] gpk;                    //h1gsk，因为h2gsk无法验证
        uint256[4] blsGpk;

        bytes validatorPublicKey;
        bytes signature;
        bytes32 depositDataRoot;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    //// CRYPTOGRAPHIC CONSTANTS

    uint256 constant GROUP_ORDER   = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
    uint256 constant FIELD_MODULUS = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    // definition of two indepently selected generator for the GROUPs G1 and G2 over
    // the bn128 elliptic curve
    // TODO: maybe swap generators G and H
    uint256 constant G1x  = 1;
    uint256 constant G1y  = 2;
    uint256 constant H1x  = 9727523064272218541460723335320998459488975639302513747055235660443850046724;
    uint256 constant H1y  = 5031696974169251245229961296941447383441169981934237515842977230762345915487;

    // For the generator H, we need an corresponding generator in the GROUP G2.
    // Notice that generator H2 is actually given in its negated form,
    // because the bn128_pairing check in Solidty is different from the Pyhton variant.
    // H2在python中与这里是不同的
    uint256 constant H2xi = 14120302265976430476300156362541817133873389322564306174224598966336605751189;
    uint256 constant H2x  = 9110522554455888802745409460679507850660709404525090688071718755658817738702;
    uint256 constant H2yi = 337404400665185879215756363144893538418066400846800837504021992006027281794;
    uint256 constant H2y  = 13873181274231081108062283139528542484285035428387832848088103558524636808404;


    ////////////////////////////////////////////////////////////////////////////////////////////////
    //// EVENTS
    event Register(uint256 nodeIndex, address nodeAddress, uint256 clusterIndex, uint256 clusderSize);
    event CreateWithdrawalCredential(address withdrawalCredential);
    event ShareDistribution(address issuer, uint256[] encryptedShares, uint256[2][] commitments);
    event Dispute(uint256 issuer, uint256[2] sharedKey, uint256[2] sharedKeyCorrectnessProof);
    event KeyShareSubmission(address issuer, uint256[2] keyShareG1, uint256[2] keyShareG1CorrectnessProof, uint256[4] keyShareG2);
    // event Payload(address operatorAddress, bytes groupPublicKey, bytes signature, bytes32 depositDataRoot);
    // event Deposit(address[] operatorPublicKeys);
    event Deposit(uint256 groupIndex, bytes withdrawalCredential);
    event Gpkj(uint256[4] gpkj);

    ////////////////////////////////////////////////////////////////////////////////////////////////
    //// STORAGE
    
    //记录cluster与node数量
    uint256 public clusterAmount = 0;
    uint256 public nodeAmount = 0;

    //constant
    bytes1 constant ETH1_ADDRESS_WITHDRAWAL_PREFIX = 0x01;
    
    // maps storing information required to perform in-contract validition for each registered node
    mapping(uint256 => Cluster) public clusters;    // uint256 = nodeAmount
    mapping(uint256 => Node) public nodes;          // uint256 = nodePublicKey[0] = publicKey.x
    


    ////////////////////////////////////////////////////////////////////////////////////////////////
    //// MAIN CONTRACT FUNCTIONS  

    function register(uint256 listIdx, uint256 clusterSize, uint256[2] memory nodePublicKey) public payable {     
        require(        // cluster size valid?
            clusterSize == 4 || clusterSize == 7 || clusterSize == 10 || clusterSize == 13, 
            "Invalid cluster size"
        );
        
        require(      // value valid?
            msg.value == 2000000000000000 wei, 
            "Deposit must be exactly 2000000000000000 wei ETH"
        );
        

        require(        //  registed?
            nodes[nodePublicKey[0]].nodeAddress == address(0),            
            "registration failed (account already registered a public key)"
        );
        require(        // on curve?
            bn128_is_on_curve(nodePublicKey),
            "registration failed (public key not on elliptic curve)"
        );
        
        
        // 加入新节点需要判断是否创建新的cluster
        if(clusterAmount == 0 || clusters[clusterAmount].clusterNodesAmount == clusterSize){     
            clusterAmount++;

            Cluster memory tmp;
            tmp.clusterIndex = clusterAmount;
            tmp.clusterSize = clusterSize;
            tmp.clusterNodesAmount = 0;
            tmp.nodePublicKeyXs = new uint256[](clusterSize);
            tmp.shareDistributionHashes = new bytes32[](clusterSize);
            tmp.commitments1stCoefficients = new uint256[2][](clusterSize);
            tmp.keyShares = new uint256[2][](clusterSize);
            tmp.laggingTrigExit = 0;

            clusters[clusterAmount] = tmp;
            
        }

        nodeAmount++;
        Cluster storage clusterCur = clusters[clusterAmount];           //当前的cluster
        

        // 新节点存入 mapping(uint256 => Node) public nodes
        nodes[nodePublicKey[0]] = Node({
            nodeIndex: nodeAmount,
            nodeAddress: msg.sender,
            clusterIndex: clusterAmount,
            clusterSize: clusterSize,

            // DKG info
            nodePublicKey : nodePublicKey,
            shareDistributionHash: bytes32(0),
            commitments1stCoefficient : [uint256(0), uint256(0)],
            keyShare : [uint256(0), uint256(0)],
            masterPublicKey : [uint256(0), uint256(0), uint256(0), uint256(0)],
            gpk : [uint256(0), uint256(0)],
            blsGpk : [uint256(0), uint256(0), uint256(0), uint256(0)],

            validatorPublicKey: new bytes(0),
            signature: new bytes(0),
            depositDataRoot: bytes32(0)
        });
        // 新节点信息存入对应的cluster中
        clusterCur.nodePublicKeyXs[listIdx] = nodePublicKey[0];
        clusterCur.clusterNodesAmount = clusterCur.clusterNodesAmount + 1;

        emit Register(nodeAmount, msg.sender, clusterAmount, clusterSize);
    }


    function distributeShares(
        uint8 listIdx, 
        uint256 publicKeyX, 
        uint256[] memory encryptedShares, 
        uint256[2][] memory commitments) public{   // 没有做访问控制 --> 可以冒充其他节点

        
            Node storage nodeCur = nodes[publicKeyX];      //当前node
            Cluster storage clusterCur = clusters[nodeCur.clusterIndex];    //当前cluster
            
            require(                                                       // 确保DKG信息顺序与注册先后顺序相同
                clusterCur.nodePublicKeyXs[listIdx] == publicKeyX, 
                "distributeShares failed (listIdx not matches publicKeyX)"
            );

            // uint256 n = nodeCur.clusterSize;
            // uint256 t = 2 * (n / 3) + 1;                  //t == quorum                                      

            /*
            require(
                (T_REGISTRATION_END < block.number) && (block.number <= T_SHARE_DISTRIBUTION_END),
                "share distribution failed (contract is not in share distribution phase)"
            );
            */
            require(      // registered or submitted?
                validityShareDistribution(publicKeyX), 
                "share distribution failed (ethereum account has not registered or has submitted)"
            );
            /* 测试阶段，只传入一个值
            require(
                encryptedShares.length == n - 1,
                "share distribution failed (invalid number of encrypted shares provided)"
            );
            require(
                commitments.length == t,
                "key sharing failed (invalid number of commitments provided)"
            );
            
            for (uint256 k = 0; k < t; k ++) {
                require(
                    bn128_is_on_curve(commitments[k]),
                    "key sharing failed (commitment not on elliptic curve)"
                );
            }
            */

        //shareDistributionHash分别存入node于cluster
            nodeCur.shareDistributionHash = keccak256(                        
                abi.encodePacked(encryptedShares, commitments)
            );
            nodeCur.commitments1stCoefficient = commitments[0];

            clusterCur.shareDistributionHashes[listIdx] = keccak256(                      
                abi.encodePacked(encryptedShares, commitments)
            );
            clusterCur.commitments1stCoefficients[listIdx] = commitments[0];

            emit ShareDistribution(msg.sender, encryptedShares, commitments);
    }

    

    function submitDispute(
        uint256 issuerPublicKeyX,                                                           // nodes that publish wrong share&commitments
        uint256 disputerPublicKeyX,                                                         // publicKey.x of disputer          
        uint8 issuerListIdx,
        uint8 disputerListIdx,                                                          // 发起dispute的node        
        uint256[] memory encrypted_shares,
        uint256[2][] memory commitments,
        uint256[2] memory sharedKey,
        uint256[2] memory sharedKeyCorrectnessProof) public {

            Node storage nodeIssuerCur = nodes[issuerPublicKeyX];                 // 当前nodeIsser
            Node storage nodeDisputerCur = nodes[disputerPublicKeyX]; 
            Cluster storage clusterCur = clusters[nodeIssuerCur.clusterIndex];    // 当前cluster
            /*
            require(
                (T_SHARE_DISTRIBUTION_END < block.number) && (block.number <= T_DISPUTE_END),
                "dispute failed (contract is not in dispute phase)"
            );
            */
            require(
                clusterCur.nodePublicKeyXs[issuerListIdx] == issuerPublicKeyX &&                   
                clusterCur.nodePublicKeyXs[disputerListIdx] == disputerPublicKeyX,
                "dispute failed (invalid list indices)"
            );

            // Check if a other node already submitted a dispute against the same issuer.
            // In this case the issuer is already disqualified and no further actions are required here.
            if (clusterCur.shareDistributionHashes[issuerListIdx] == 0) {
                return;
            }

            require(            // 验证disputer提供的share与commitment是否正确                                                      
                clusterCur.shareDistributionHashes[issuerListIdx] == keccak256(                  
                    abi.encodePacked(encrypted_shares, commitments)
                ),
                "dispute failed (invalid replay of sharing transaction)"
            );
            require(            // 验证kij是否正确; 不排除kij是disputer伪造的，即故意发起dispute
                /* dleq_verify(
                    [H1x, H1y],         //h1
                    keyShareG1,       //h1^si
                    [G1x, G1y],         //g1
                    nodeCur.commitments1stCoefficient,        //g1^si
                    keyShareG1CorrectnessProof              //Π
                ),*/
                dleq_verify(                                                                    
                    nodeIssuerCur.nodePublicKey,        // pki
                    sharedKey,                          // kij
                    [G1x, G1y],                         // g1
                    nodeDisputerCur.nodePublicKey,      // pkj
                    sharedKeyCorrectnessProof           // Π
                ),
                "dispute failed (invalid shared key or proof)"                  
            );

            // Since all provided data is valid so far, we load the share and use the verified shared
            // key to decrypt the share for the disputer.
            uint256 share= encrypted_shares[disputerListIdx];

            uint256 disputer_idx = disputerListIdx;       // fi(x)中的x = disputer_idx;
            if (disputerListIdx < issuerPublicKeyX) {          // 假设disputer_list_idx = 0, issuer_list_idx =3
                share = encrypted_shares[disputerListIdx];    // enc_shares中是不包含自己发给自己的。enc_shares.len = addresses.len - 1 = n - 1
            }                                                   // enc_shares:3 -> 1        
           else {
                share = encrypted_shares[disputerListIdx - 1];
            }
                         
            uint256 decryption_key = uint256(keccak256(
                abi.encodePacked(sharedKey[0], disputer_idx)   // H(kij + j):因为disputer是接收方，所以 j == x == disputer_idx
            ));
            share ^= decryption_key;                        //得到解密之后的share
            
            // Verify the share for it's correctness using the polynomial defined by the commitments.
            // First, the polynomial (in group G1) is evaluated at the disputer's idx.
            
            uint256 x = disputer_idx;
            uint256[2] memory result = commitments[0];
            uint256[2] memory tmp = bn128_multiply([commitments[1][0], commitments[1][1], x]);
            result = bn128_add([result[0], result[1], tmp[0], tmp[1]]);
            for (uint256 j = 2; j < commitments.length; j += 1) {
                x = mulmod(x, disputer_idx, GROUP_ORDER);                   // x, x^2, x^3,........
                tmp = bn128_multiply([commitments[j][0], commitments[j][1], x]);
                result = bn128_add([result[0], result[1], tmp[0], tmp[1]]);
            }
            // Then the result is compared to the point in G1 corresponding to the decrypted share.
            tmp = bn128_multiply([G1x, G1y, share]);                    // tmp = g1^share
            require(
                result[0] != tmp[0] || result[1] != tmp[1],             // result = Fi(j)
                "dispute failed (the provided share was valid)"         // 如果都是 == 的话，说明dispute是错误的，issuer是对的。
            );
            
            // We mark the nodes as disqualified by setting the distribution hash to 0. This way the
            // case of not proving shares at all and providing invalid shares can be handled equally.
            uint8 ilistIdx = issuerListIdx;                                         // 因为有stack too steep的问题，加上这句话就没问题了                                
            clusterCur.shareDistributionHashes[ilistIdx] = 0;
            nodeIssuerCur.shareDistributionHash = 0;
            emit Dispute(ilistIdx, sharedKey, sharedKeyCorrectnessProof);   // CompilerError
    }


    function submitKeyShare(
        uint8 listIdx,
        uint256 publicKeyX,
        uint256[2] memory keyShareG1,             
        uint256[2] memory keyShareG1CorrectnessProof,
        uint256[4] memory keyShareG2) public {

            Node storage nodeCur = nodes[publicKeyX];      //当前node
            Cluster storage clusterCur = clusters[nodeCur.clusterIndex];

            require(                                                       // 确保DKG信息顺序与注册先后顺序相同
                clusterCur.nodePublicKeyXs[listIdx] == publicKeyX, 
                "distributeShares failed (listIdx not matches publicKeyX)"
            );

            /*
            require(
                (T_DISPUTE_END < block.number),
                "key share submission failed (contract is not in key derivation phase)"
            );
            if (key_shares[issuer][0] != 0) {
                // already submitted, no need to resubmit
                return;
            }
            require(
                share_distribution_hashes[issuer] != 0,
                "key share submission failed (issuer not qualified)"
            );
            */
            require(    // dleq_verify
                dleq_verify(
                    [H1x, H1y],         //h1
                    keyShareG1,       //h1^si
                    [G1x, G1y],         //g1
                    nodeCur.commitments1stCoefficient,        //g1^si
                    keyShareG1CorrectnessProof              //Π
                ),
                "key share submission failed (invalid key share (G1))"
            );
            require(    // bn128_check_pairing

                bn128_check_pairing([
                    keyShareG1[0], keyShareG1[1],
                    H2xi, H2x, H2yi, H2y,
                    H1x, H1y,
                    keyShareG2[0], keyShareG2[1], keyShareG2[2], keyShareG2[3]
                ]),
                "key share submission failed (invalid key share (G2))"
            );

            nodes[publicKeyX].keyShare = keyShareG1;
            clusterCur.keyShares[listIdx] = keyShareG1;           // msg.sender都是同一个账户 --> keyShares遭到覆盖

            // emit KeyShareSubmission(issuer, keyShareG1, keyShareG1CorrectnessProof, keyShareG2);
    }
   
    
    function submitMasterPublicKey(  
        uint256 publicKeyX,
        uint256[4] memory masterPublicKey) public {
        
            /*
            require(
                (T_DISPUTE_END < block.number),
                "master key submission failed (contract is not in key derivation phase)"
            );
            if (master_public_key[0] != 0) {        // 判断是否已经有人提交过公钥
                return;
            }
            */
            Node storage nodeCur = nodes[publicKeyX];      //当前node
            Cluster storage clusterCur = clusters[nodeCur.clusterIndex];    //当前cluster
            uint256 n = clusterCur.nodePublicKeyXs.length;               //参与的节点数量

            // find first (i.e. lowest index) node contributing to the final key
            uint256[2] memory tmp;                    
            uint256[2] memory mpk_G1;

            uint8 i = 0;
            for (; i < n; i++) {           // 计算mpk_G1            
                if (clusterCur.shareDistributionHashes[i] == 0) {         // 跳过非法的节点
                    continue;
                }
                tmp = clusterCur.keyShares[i];
                require(tmp[0] != 0, 'master key submission failed (key share missing)');
                if (i == 0) {
                    mpk_G1 = tmp;
                }
                else {
                    mpk_G1 = bn128_add([mpk_G1[0], mpk_G1[1], tmp[0], tmp[1]]);
                }
            }

            require(        // bn128_check_pairing
                bn128_check_pairing([
                    mpk_G1[0], mpk_G1[1],                        // 
                    H2xi, H2x, H2yi, H2y,                        // h2
                    H1x, H1y,                                    // h1
                    masterPublicKey[0], masterPublicKey[1],
                    masterPublicKey[2], masterPublicKey[3]       // 
                ]),
                'master key submission failed (pairing check failed)'
            );

            //node, cluster存入bn128PK
            nodeCur.masterPublicKey = masterPublicKey;
            clusterCur.masterPublicKey = masterPublicKey;
    }

    function submitGpkj(
        uint256 publicKeyX,
        uint256 listIdx,
        uint256[2] memory ggskj,                    // 
        uint256[][] memory encrypted_sharesQ,       // Σi∈Q(si->j) : [n][Q]
        uint256[2][][] memory commitmentsQ,         // Πi∈Q{Fi(j)} : [2][t][Q] 
        uint256[2] memory h1gpkj,                   
        uint256[2] memory h1gpkjCorrectnessProof,
        uint256[4] memory h2gpkj                    //node's self bls_pk
        ) public {

            // 0. 常规检查
            // 验证发起者是否属于Q集合
            // 验证listIdx是否正确

            Node storage nodeCur = nodes[publicKeyX];
            Cluster storage clusterCur = clusters[nodeCur.clusterIndex];
            // // 1. 验证ggskj
            // // 验证是否篡改encrypted_shares与commitments
            for (uint i = 0; i < clusterCur.clusterSize; i++) 
            {
                if (clusterCur.shareDistributionHashes[i] == 0 || 
                    clusterCur.shareDistributionHashes[i] == 
                        keccak256(abi.encodePacked(encrypted_sharesQ[i], commitmentsQ[i]))) {
                            continue;
                }
                assert(false);
            }

            // 验证g^gskj是否 == Π(Fi(j)
            // : 需要计算的是share不是enc_share
            // : 且计算的是share不是shares
            // TODO : 解密enc_shares -> shares
            
            uint256[2] memory result;
            uint256 x;                  // x为j的值; si(j)中的j是不会改变的; j == listIdx
            uint256[2] memory tmp;
            for (uint i = 0; i < clusterCur.clusterSize; i++) 
            {
                if (clusterCur.shareDistributionHashes[i] == 0){        // 遭受dispute成功的或者本身为0, 跳过
                    continue ;
                }

                x = listIdx;                            // x需要重新赋值
                if (i == 0) {
                    result = commitmentsQ[i][0]; 
                } else {
                    result = bn128_add([result[0], result[1], commitmentsQ[i][0][0], commitmentsQ[i][0][1]]);
                }       
                tmp = bn128_multiply([commitmentsQ[i][1][0], commitmentsQ[i][1][1], x]);
                result = bn128_add([result[0], result[1], tmp[0], tmp[1]]);
                for (uint256 j = 2; j < commitmentsQ[i].length; j += 1) {
                    x = mulmod(x, listIdx, GROUP_ORDER);                   // x^2, x^3,........
                    tmp = bn128_multiply([commitmentsQ[i][j][0], commitmentsQ[i][j][1], x]);
                    result = bn128_add([result[0], result[1], tmp[0], tmp[1]]);
                }
            }
            require(
                ggskj[0] == result [0] && ggskj[1] == result[1], 
                "ggskj doesn't match the commitmentsQ"
            );

    
            // 2. DLEQ-VERIFY验证h1gpkjCorrectnessProof
            require(                // DLEQ(g; ggskj; h; gpkj; gskj) 
                dleq_verify(                                                                    
                    [H1x, H1y],        
                    h1gpkj,                         
                    [G1x, G1y],                         
                    ggskj,      
                    h1gpkjCorrectnessProof           
                ),
                "submitGpkj failed (invalid h1gpkj Correctness Proof)"                  
            );


            // 3. paring验证h2gpkj
            require(        // bn128_check_pairing
                bn128_check_pairing([
                    h1gpkj[0], h1gpkj[1],                        // 
                    H2xi, H2x, H2yi, H2y,                        // h2
                    H1x, H1y,                                    // h1
                    h2gpkj[0], h2gpkj[1],
                    h2gpkj[2], h2gpkj[3]       // 
                ]),
                "submitGpkj failed (pairing check failed)"
            );
            // 将h1gpkj存入node中
            nodeCur.gpk = h1gpkj;
            nodeCur.blsGpk = h2gpkj;


            emit Gpkj(h2gpkj);
    }


    function depositToGoerli(                           
            uint256 publicKeyX,                     
            uint256[2] calldata signature,              // G1
            uint256[2] calldata depositMessage                 // G1
            // bytes32 depositDataRoot
            ) public {
        
            // 0. 常规检查
            // require publicKeyX
            // require masterKey ！=0               signature需要在masterKey正确之后才能提交

            Node storage nodeCur = nodes[publicKeyX];      //当前node
            Cluster storage clusterCur = clusters[nodeCur.clusterIndex];

            // 1. 检查签名
            // require(signature.length == 96, "DepositContract: invalid signature length");

            // 公钥验证签名是否正确: 因为公私钥的唯一性 --> 同时保证message与signature的正确性
            require( 
                bn128_check_pairing([
                    signature[0], signature[1],                  // h1^(si_0 + …… + si_n)
                    H2xi, H2x, H2yi, H2y,                        // h2
                    depositMessage[0], depositMessage[1],                                    // h1
                    nodeCur.masterPublicKey[0], nodeCur.masterPublicKey[1],
                    nodeCur.masterPublicKey[2], nodeCur.masterPublicKey[3]       // h2^(si_0 + …… + si_n)
                    
                ]),
                'signature does not match the masterPublicKey'
            );
            

            //2. deposit
            // 创建withdrawal credential
            address payable[4] memory stakers;          // 测试用
            for (uint i = 0; i < clusterCur.clusterSize; i++) 
            {
                address payable nodeAddress = payable(nodes[clusterCur.nodePublicKeyXs[i]].nodeAddress);
                stakers[i] = nodeAddress;
            }
            clusterCur.withdrawalCredential = createWithdrawalCredential(
                address(this), 
                stakers);
            emit CreateWithdrawalCredential(clusterCur.withdrawalCredential);

            // 需要将智能合约地址转换成ETH1 withdrawal credential
            bytes memory withdrawalCredential = convertToWithdrawalCredential(clusterCur.withdrawalCredential);  


            // TODO:调用goerli上的deposit合约
            // goerliDeposit.deposit(clusterCur.masterPublicKey, withdrawalCredential, signature, depositDataRoot);
            // 仅测试 --> 将32ETH转到withdrawalCredential的地址中; 不进行注册validator的过程
            (bool success, ) = clusterCur.withdrawalCredential.call{value: 8000000000000000 wei}("");
            require(success, "Transfer to withdrawalCredential failed");
        

            emit Deposit(clusterCur.clusterIndex, withdrawalCredential);
    }

    
    function normalExit(
        uint256 publicKeyX, 
        uint256[] memory balanceInfo,              // 余额分配信息
        uint256[2] memory signature) public  {

            // 0. 常规检查

            Node storage nodeCur = nodes[publicKeyX];
            Cluster storage clusterCur = clusters[nodeCur.clusterIndex];

            // 1. 计算H(m)
            uint256[2] memory Hbalance = mapToBn128G1(balanceInfo);     // G1

            // 2. 检查签名
           require( 
                bn128_check_pairing([
                    signature[0], signature[1],                  // h1^(si_0 + …… + si_n)
                    H2xi, H2x, H2yi, H2y,                        // h2
                    Hbalance[0], Hbalance[1],                                    // h1
                    nodeCur.masterPublicKey[0], nodeCur.masterPublicKey[1],
                    nodeCur.masterPublicKey[2], nodeCur.masterPublicKey[3]       // h2^(si_0 + …… + si_n)
                ]),
                'exit failed (signature does not match the masterPublicKey)'
            );


            // 3. 将balance信息发送至withdrawal合约
            (bool success, ) = clusterCur.withdrawalCredential.call(
            abi.encodeWithSignature("fund(uint256[])", balanceInfo));
            require(success, "BalanceInfo to withdrawalCredential failed");

            // 4. TODO：删除cluster与节点信息
    }


    function slashExit(
        uint256 listIdx,
        uint256 publicKeyX, 
        uint256[][2] memory slashContents,       // double vote content;slashContents[0]与slashContents[1];例如v与v'
        uint256[2][2] memory slashProof,       // double vote proof;对double vote的不同的muti-signature;多重签名能够减少验证次数

        uint256[] memory faultyPublicKeyX,            // faultyPublicKeyX,从而计算出muti-pk
        uint256[4] memory mutiBlsPK,              // paring

        uint256[2][2] memory slashContentsSignature,       // slashProof用于确认参与方; signature用于证明确实对slashContents中的内容都达成了共识
        
        uint256[] memory balanceInfo,               // 余额分配信息
        uint256[2] memory balanceInfoSignature)     // multi-sig 
        public {

            // 0. 常规检查

            Node storage nodeCur = nodes[publicKeyX];
            Cluster storage clusterCur = clusters[nodeCur.clusterIndex];


            // 1. 验证signature与slashProof
            // 计算muti-multiGpk
            uint256[2] memory multiGpk = nodes[faultyPublicKeyX[0]].gpk;
            
            for (uint i = 1; i < faultyPublicKeyX.length; i++) 
            {
                multiGpk = bn128_add([multiGpk[0], multiGpk[1], nodes[faultyPublicKeyX[i]].gpk[0], nodes[faultyPublicKeyX[i]].gpk[1]]);
            }
    
            require( //验证mutiBlsPK，因为bn128不支持G2，所以使用paring验证
                bn128_check_pairing([
                    multiGpk[0], multiGpk[1],                  
                    H2xi, H2x, H2yi, H2y,                   
                    H1x, H1y,                                   
                    mutiBlsPK[0], mutiBlsPK[1],
                    mutiBlsPK[2], mutiBlsPK[3]       
                    
                ]),
                'smutiBlsPK not match the multiGpk'
            );
            
            uint256[2] memory HslashContent;
            // 验证signature与slashProof
            // TODO:将sig-->multisig, 去掉for循环
            for (uint i = 0; i < 2; i++) 
            {
                // 计算H(slashContents)
                HslashContent = mapToBn128G1(slashContents[i]);     //**************可能换导致keccack值不同

                // 验证signature
                require( 
                bn128_check_pairing([
                    slashContentsSignature[i][0], slashContentsSignature[i][1],                  
                    H2xi, H2x, H2yi, H2y,                        
                    HslashContent[0], HslashContent[1],                                   
                    clusterCur.masterPublicKey[0], clusterCur.masterPublicKey[1],
                    clusterCur.masterPublicKey[2], clusterCur.masterPublicKey[3]    
                ]),
                'signature does not match the masterPublicKey'
                );

                // 验证slashProof：muti-signature       这里出错了
                require( 
                bn128_check_pairing([
                    slashProof[i][0], slashProof[i][1],                  // h1^(si_0 + …… + si_n)
                    H2xi, H2x, H2yi, H2y,                        // h2
                    HslashContent[0], HslashContent[1],                                    // h1
                    mutiBlsPK[0], mutiBlsPK[1],
                    mutiBlsPK[2], mutiBlsPK[3]       // h2^(si_0 + …… + si_n)
                    
                ]),
                'signature0 does not match the masterPublicKey'
                );
            }  

            // 2. 将balanceInfo发送至withdrawal合约
            // 1. 计算H(m)
            uint256[2] memory Hbalance = mapToBn128G1(balanceInfo);     // G1

            // 2. 检查签名
           require( 
                bn128_check_pairing([
                    balanceInfoSignature[0], balanceInfoSignature[1],    
                    H2xi, H2x, H2yi, H2y,                        // h2
                    Hbalance[0], Hbalance[1],                                    // h1
                    clusterCur.masterPublicKey[0], clusterCur.masterPublicKey[1],       // 这里有问题，这里仍然使用了Q个人的聚合签名
                    clusterCur.masterPublicKey[2], clusterCur.masterPublicKey[3]       // h2^(si_0 + …… + si_n)
                ]),
                'exit failed (signature does not match the masterPublicKey)'
            );

            // 发送balanceInfo
            (bool success, ) = clusterCur.withdrawalCredential.call(
            abi.encodeWithSignature("fund(uint256[])", balanceInfo));
            require(success, "BalanceInfo to withdrawalCredential failed");

        //     // 4. TODO：删除cluster与节点信息
    }
    
    function laggingTrigExit(
        uint256 publicKeyX,
        uint256 listIdx,
        uint256[] memory exitInfo,              // 包含了balanceInfo
        uint256[] memory exitInfoSig

    ) public {
        Node storage nodeCur = nodes[publicKeyX];
        Cluster storage clusterCur = clusters[nodeCur.clusterIndex];

        // 0. 常规检查
        

        if (clusterCur.laggingTrigExit == 0) {
            // laggingTrigExit开启----------------> 需要设置标志

            clusterCur.laggingTrigExit++;
        }

        // 1. 检查签名
        // 计算H(m)
        uint256[2] memory HExitInfo = mapToBn128G1(exitInfo);     // G1

        // TODO : exitINFO必须包含exit的正确内容，必须得检查

        require(
            bn128_check_pairing([
                exitInfoSig[0], exitInfoSig[1],                  // h1^(si_0 + …… + si_n)
                H2xi, H2x, H2yi, H2y,                        // h2
                HExitInfo[0], HExitInfo[1],                                    // h1
                nodeCur.blsGpk[0], nodeCur.blsGpk[1],
                nodeCur.blsGpk[2], nodeCur.blsGpk[3]       // h2^(si_0 + …… + si_n)
            ]),
            'exit failed (signature does not match the masterPublicKey)'
        );    

        // 2. refund 
        // 返还exit fund
        // 发起交易的时间是否在规定范围内
        if (true) {    
            (bool success, ) = clusterCur.withdrawalCredential.call(
            abi.encodeWithSignature("fundExit(uint256)", listIdx));
            require(success, "fundExit to withdrawalCredential failed");
        } else {
            // 补偿给其他节点一定的fund，剩余的分给自己

        }

        // 返还stake fund                
        // if (clusterCur.laggingTrigExit == clusterCur.clusterSize) {
            
        // }
    }

    
    
    
    ////////////////////////////////////////////////////////////////////////////////////////////////
    //// Utils        

    //创建取款凭证
    function createWithdrawalCredential(address stakingPool, address payable[4] memory stakers) internal returns (address)  {
        address _withdrawalCredential = address(new WithdrawalCredential(stakingPool, stakers));
        return  _withdrawalCredential;
    }

    // 查看合约余额的函数
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

   
    function validityShareDistribution(uint256 sender) internal view returns (bool) {
        if (nodes[sender].nodePublicKey[0] == sender) {        //已经注册
            if (nodes[sender].shareDistributionHash == bytes32(0)) {   //还未提交share
                return true;
            }    
        }
        return false;
    }


    // 智能合约地址转换成ETH1 withdrawal credential
    function convertToWithdrawalCredential(address ethAddress) internal pure returns (bytes memory) {
        bytes memory withdrawalCredential = new bytes(32);

        withdrawalCredential[0] = ETH1_ADDRESS_WITHDRAWAL_PREFIX;
        // The next 11 bytes are already initialized to 0x00

        // Copy the Ethereum address bytes to the withdrawal credential
        for (uint256 i = 0; i < 20; i++) {
            withdrawalCredential[12 + i] = bytes1(uint8(uint160(ethAddress) / (2 ** (8 * (19 - i)))));
        }

        return withdrawalCredential;
    }

    function bn128_is_on_curve(uint256[2] memory point)
    private pure returns(bool)
    {
        // check if the provided point is on the bn128 curve (y**2 = x**3 + 3)
        return
            mulmod(point[1], point[1], FIELD_MODULUS) ==
            addmod(
                mulmod(
                    point[0],
                    mulmod(point[0], point[0], FIELD_MODULUS),
                    FIELD_MODULUS
                ),
                3,
                FIELD_MODULUS
            );
    }

    function dleq_verify(
        uint256[2] memory x2, uint256[2] memory y2,             // 将x2,y2与x1,y1的顺序调换了
        uint256[2] memory x1, uint256[2] memory y1,
        uint256[2] memory proof) private returns (bool proof_is_valid) {

            //  dleq_verify(
            //         [H1x, H1y],         //h1
            //         keyShareG1,       //h1si
            //         [G1x, G1y],         //g1
            //         nodes[issuer].commitments1stCoefficient,        //g1si
            //         keyShareG1CorrectnessProof              //Π
            //     ),
            uint256[2] memory tmp1;
            uint256[2] memory tmp2;

            tmp1 = bn128_multiply([x1[0], x1[1], proof[1]]);    //x1 = h1
            tmp2 = bn128_multiply([y1[0], y1[1], proof[0]]);    //y1 = h1si
            uint256[2] memory a1 = bn128_add([tmp1[0], tmp1[1], tmp2[0], tmp2[1]]);

            tmp1 = bn128_multiply([x2[0], x2[1], proof[1]]);    //x2 = g1
            tmp2 = bn128_multiply([y2[0], y2[1], proof[0]]);    //y2 = g1si
            uint256[2] memory a2 = bn128_add([tmp1[0], tmp1[1], tmp2[0], tmp2[1]]);

            uint256 challenge = uint256(keccak256(abi.encodePacked(a1, a2, x1, y1, x2, y2)));
            proof_is_valid = (challenge == proof[0]);
    }

    function bn128_add(uint256[4] memory input)
    internal  returns (uint256[2] memory result) {
        // computes P + Q
        // input: 4 values of 256 bit each
        //  *) x-coordinate of point P
        //  *) y-coordinate of point P
        //  *) x-coordinate of point Q
        //  *) y-coordinate of point Q

        bool success;
        assembly {
            // 0x06     id of precompiled bn256Add contract
            // 0        number of ether to transfer
            // 128      size of call parameters, i.e. 128 bytes total
            // 64       size of call return value, i.e. 64 bytes / 512 bit for a BN256 curve point
            success := call(not(0), 0x06, 0, input, 128, result, 64)
        }
        require(success, "elliptic curve addition failed");
    }

    function bn128_multiply(uint256[3] memory input)
    internal  returns (uint256[2] memory result) {
        // computes P*x
        // input: 3 values of 256 bit each
        //  *) x-coordinate of point P
        //  *) y-coordinate of point P
        //  *) scalar x

        bool success;
        assembly {
            // 0x07     id of precompiled bn256ScalarMul contract
            // 0        number of ether to transfer
            // 96       size of call parameters, i.e. 96 bytes total (256 bit for x, 256 bit for y, 256 bit for scalar)
            // 64       size of call return value, i.e. 64 bytes / 512 bit for a BN256 curve point
            success := call(not(0), 0x07, 0, input, 96, result, 64) 
        }
        require(success, "elliptic curve multiplication failed");
    }

    function bn128_check_pairing(uint256[12] memory input)
    internal  returns (bool) {
        uint256[1] memory result;
        bool success;
        assembly {
            // 0x08     id of precompiled bn256Pairing contract     (checking the elliptic curve pairings)
            // 0        number of ether to transfer
            // 384       size of call parameters, i.e. 12*256 bits == 384 bytes
            // 32        size of result (one 32 byte boolean!)
            success := call(sub(gas(), 2000), 0x08, 0, input, 384, result, 32)
        }
        require(success, "elliptic curve pairing failed");
        return result[0] == 1;
    }

    function mapToBn128G1(uint256[] memory input) internal  returns (uint256[2] memory result){
        uint256 scalar = uint256(keccak256(abi.encodePacked(input)));
        result = bn128_multiply([G1x, G1y, scalar]);
    }

    receive() external payable {
        // 在这里处理接收到的以太币
    }
}




