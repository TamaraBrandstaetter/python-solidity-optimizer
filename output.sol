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
        uint256 var_437a108df1924d61967b7fee98bf5810 = someExpensiveOperation();
        for (uint256 i = 0; i < 12; i++) {
            array[i] = i + var_437a108df1924d61967b7fee98bf5810 + 12;
        }
    }
	
	function doSomethingAgain() public {
        uint256[] memory array = new uint256[](10);
        uint256 var_f7d69b45af394cc2b50b231049e825de = someExpensiveOperation();
        for (uint256 i = 0; i < 22; i++) {
            array[i] = var_f7d69b45af394cc2b50b231049e825de;
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
