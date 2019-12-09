pragma solidity ^0.5.12;

contract Loop1 {
	function doSomething1() public returns(uint256) {
		uint256 a = 123;
		for(uint256 i = 0; i < 100; i++) {
		}
		return 12;
	}
	
    function doSomething() public {
        uint256[] memory array = new uint256[](10);
        uint256 var_01cb4ad3d554419190ea6e5642e55b9a = someExpensiveOperation();
        for (uint256 i = 0; i < 12; i++) {
            array[i] = i + var_01cb4ad3d554419190ea6e5642e55b9a + 12;
        }
    }
	
	function doSomethingAgain() public {
        uint256[] memory array = new uint256[](10);
        uint256 var_8b0b604103ea42e9b1fde32ad6a19897 = someExpensiveOperation();
        for (uint256 i = 0; i < 22; i++) {
            array[i] = var_8b0b604103ea42e9b1fde32ad6a19897;
        }
    }
    
    function someExpensiveOperation() private pure returns(uint256) {
        return sqrt(199) + sqrt(234) * 212 - 234;
    }
	
	function test(uint a) private pure returns(uint256) {
		return 2356;
	}
    
    function sqrt(uint256 x) private pure returns (uint256 y) {
        uint z = (x + 1) / 2;
        y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
    }
}
