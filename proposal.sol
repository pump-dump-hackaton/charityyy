// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;

contract Proposal {
    struct Expense{
        address buisness_address;
        uint amount;
    }

    Expense[] public expenses;
    address public originator;
    uint public funds_raised;
    uint immutable public goal;

    // constructor(address[] memory buisness_addresses, uint[] memory amounts){
    //     originator = msg.sender;
    //     require(buisness_addresses.length == amounts.length);

    //     for (uint i = 0; i < buisness_addresses.length; i++) {
    //         expenses.push(Expense({
    //             buisness_address: buisness_addresses[i],
    //             amount: amounts[i]
    //         }));
    //         goal += amounts[i];
    //     }
    // }

    constructor(address buisness_addresses, uint amounts){
        originator = msg.sender;
        // require(buisness_addresses == amounts);

        for (uint i = 0; i < 1; i++) {
            expenses.push(Expense({
                buisness_address: buisness_addresses,
                amount: amounts
            }));
            goal += amounts;
        }  
    }

    // function releaseFunds() private {
    //     require(funds_raised==goal);

    //     for (uint i = 0; i < expenses.length; i++) {
    //         Expense memory e = expenses[i];
    //         //send the money for the buinsess and it coressponding money
    //         (bool success, ) = e.buisness_address.call{value: e.amount}("");
    //         require(success, "Payment to business failed");
    //     }
    // }

    function donate() public payable  {
        uint donation = msg.value;
        funds_raised += donation;

        // if (funds_raised + donation > goal) {
        //     // if person donated more then needed
        //     uint excess = funds_raised + donation - goal;
        //     funds_raised = goal;

        //     // return the excess
        //     (bool success, ) = msg.sender.call{value: excess}("");
        //     require(success, "Refund Failed");
        //     releaseFunds();
        // }else{
        //     funds_raised += donation;
        // }
    }
}

