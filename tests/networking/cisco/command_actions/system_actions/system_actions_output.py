# flake8: noqa
SUCCESS_OUTPUT = """N6K-Sw1-S1# copy running-config tftp:
        Enter destination filename: [N6K-Sw1-S1-running-config] TestName
        Enter vrf (If no input, current vrf 'default' is considered): management
        Enter hostname for the tftp server: 10.10.10.10Trying to connect to tftp server......
        Connection to Server Established.

        [                         ]         0.50KB
        [#                        ]         4.50KB

         TFTP put operation was successful
         Copy complete, now saving to disk (please wait)...

        N6K-Sw1-S1#"""


SUCCESS_OUTPUT_IOS = """C6504e-1-CE7#copy running-config tftp:
        Address or name of remote host []? 10.10.10.10
        Destination filename [c6504e-1-ce7-confg]? 6504e1
        !!
        23518 bytes copied in 0.904 secs (26015 bytes/sec)
        C6504e-1-CE7#"""


ERROR_OPENING_OUTPUT = """ASR1004-2#copy running-config tftp:
        Address or name of remote host []?
        10.10.10.10
        Destination filename [asr1004-2-confg]?
        ASR1004-2-running-100516-084841
        .....
        %Error opening tftp://10.10.10.10/ASR1004-2-running-100516-084841 (Timed out)
        ASR1004-2#"""

ERROR_ACCESS_VIOLATION = """sw9003-vpp-10-3# copy running-config tftp://10.87.42.120
        Enter destination filename: [sw9003-vpp-10-3-running-config] 123123
        Enter vrf (If no input, current vrf 'default' is considered):
        Trying to connect to tftp server......
        Connection to Server Established.
        TFTP put operation failed:Access violation"""

SUCCESS_OUTPUT_CONFIG_OVERRIDE = """changename#
        configure replace ftp://Cloudshell:KPlab123@10.233.30.222/Cloudshell/2951-2-Test-running-250817-093706
        This will apply all necessary additions and deletions
        to replace the current running configuration with the
            contents of the specified configuration file, which is
        assumed to be a complete configuration, not a partial
        configuration. Enter Y if you are sure you want to proceed. ? [no]:
        y
        Loading Cloudshell/2951-2-Test-running-250817-093706 !
        [OK - 7782/4096 bytes]

        Loading Cloudshell/2951-2-Test-running-250817-093706 !






        Total number of passes: 1
        Rollback Done

        ISR2951-2#"""


ERROR_OVERRIDE_RUNNING = """Command: configure replace ftp://admin:KPlab123@10.233.30.222/CloudShell/configs/Base/3750-1_Catalyst37xxstack.cfg
            This will apply all necessary additions and deletions
            to replace the current running configuration with the
            contents of the specified configuration file, which is
            assumed to be a complete configuration, not a partial
            configuration. Enter Y if you are sure you want to proceed. ? [no]: y
            Loading CloudShell/configs/Base/3750-1_Catalyst37xxstack.cfg !
            [OK - 3569/4096 bytes]
            Loading CloudShell/configs/Base/3750-1_Catalyst37xxstack.cfg !
            [OK - 3569/4096 bytes]
            %The input file is not a valid config file.
            37501#
            """

ERROR_ROLL_BACK = """configure replace flash:candidate_config.txt force
            The rollback configlet from the last pass is listed below:
            ********
            !List of Rollback Commands:
            adfjasdfadfa
            end
            ********
            Rollback aborted after 5 passes
            The following commands are failed to apply to the IOS image.
            ********
            adfjasdfadfa
            ********
            """

TEST_COPY_OUTPUT = """

Trying to connect to tftp server......
Connection to Server Established.

[                         ]         0.50KB
[#                        ]         4.50KB
 [##                       ]         8.50KB
  [###                      ]        12.50KB
   [####                     ]        16.50KB
    [#####                    ]        20.50KB
     [######                   ]        24.50KB
      [#######                  ]        28.50KB
       [########                 ]        32.50KB
        [#########                ]        36.50KB

         TFTP get operation was successful
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name temp FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-800 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-801 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-802 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-803 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-804 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-805 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-806 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-807 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-808 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-809 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-810 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-811 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-812 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-813 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-814 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-815 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-816 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-817 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-818 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-819 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-820 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-821 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-822 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-823 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-824 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-825 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-826 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-827 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-828 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-829 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-830 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-831 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-832 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-833 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-834 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-835 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-836 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-837 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-838 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-839 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-840 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-841 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-842 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-843 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-844 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-845 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-846 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-847 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-848 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-849 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-850 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-851 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-852 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-853 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-854 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-855 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-856 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-857 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-858 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-859 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-860 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-861 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-862 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-863 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-864 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-865 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-866 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-867 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-868 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-869 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-870 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-871 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-872 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-873 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-874 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-875 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-876 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-877 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-878 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-879 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-880 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-881 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-882 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-883 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-884 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-885 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-886 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-887 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-888 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-889 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-890 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-891 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-892 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-893 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-894 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-895 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-896 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-897 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-898 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-899 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1500 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1501 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1502 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1503 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1504 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1505 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1506 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1507 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1508 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1509 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1510 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1511 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1512 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1513 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1514 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1515 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1516 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1517 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1518 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1519 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1520 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1521 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1522 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1523 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1524 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1525 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1526 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1527 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1528 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1529 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1530 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1531 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1532 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1533 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1534 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1535 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1536 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1537 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1538 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1539 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1540 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1541 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1542 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1543 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1544 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1545 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1546 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1547 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1548 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1549 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1550 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1551 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1552 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1553 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1554 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1555 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1556 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1557 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1558 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1559 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1560 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1561 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1562 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1563 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1564 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1565 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1566 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1567 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1568 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1569 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1570 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1571 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1572 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1573 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1574 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1575 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1576 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1577 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1578 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1579 FAILED
Cannot run commands in the mode at this moment. Please try again.
Syntax error while parsing 'switchport mode trunk'

Syntax error while parsing 'switchport mode trunk'

Performing image verification and compatibility check,please wait....
Performing image verification and compatibility check,please wait....
Copy complete, now saving to disk (please wait)...
"""
