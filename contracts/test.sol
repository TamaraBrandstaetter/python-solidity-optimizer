pragma solidity ^0.5.12;

contract Loop1 {
	function doSomething1() public returns(uint256) {
		for(uint256 i = 0; i < 100; i++) {
			uint256 a = 123;
		}
		return 12;
	}
	
    function doSomething() public {
        uint256[] memory array = new uint256[](10);
        for (uint256 i = 0; i < 12; i++) {
            array[i] = i + someExpensiveOperation() + 12;
        }
    }
	
	function doSomethingAgain() public {
        uint256[] memory array = new uint256[](10);
        for (uint256 i = 0; i < 22; i++) {
            array[i] = someExpensiveOperation();
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
