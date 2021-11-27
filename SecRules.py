Sec_Rules_Database = [
    {
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22,
        'IpRanges': [
            {'CidrIp': '0.0.0.0/0'}
        ]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 5432,
        'ToPort': 5432,
        'IpRanges': [
            {'CidrIp': '0.0.0.0/0'}
        ]
    },
    {
            'FromPort': 80,
            'ToPort': 80,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {'CidrIp': '0.0.0.0/0'},
            ],
        },
]

Sec_Rules_Django = [
    {
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22,
        'IpRanges': [
            {'CidrIp': '0.0.0.0/0'}
        ]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 8080,
        'ToPort': 8080,
        'IpRanges': [
            {'CidrIp': '0.0.0.0/0'}
        ]
    },
    {
            'FromPort': 80,
            'ToPort': 80,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {'CidrIp': '0.0.0.0/0'},
            ],
        },
]
