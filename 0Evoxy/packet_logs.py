CLIENT_BET_ACCEPTED = {
    'log': {
        'type': 'CLIENT_BET_ACCEPTED', 
        'value': {
            'originalBet': {'Player': 1}, 
            'confirmed': {'Player': 1}, 
            'layout': 'ImmersiveV2', 
            'status': 'Accepted', 
            'balance': 41.72, 
            'latency': 736, 
            'bets': {'Player': 1}, 
            'gameType': 'baccarat', 
            'gameTime': '01:39:14', 
            'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', 
            'currency': 'USD', 
            'chipStack': [1, 2, 5, 25, 100, 500], 
            'tableMinLimit': 1, 
            'tableMaxLimit': 50000, 
            'gameId': '1802c8c4de8453b1c70d3a20', 
            'channel': 'PCMac', 
            'orientation': 'landscape', 
            'gameDimensions': {'width': 1066.65625, 'height': 600}
            }
           }
        } 

CLIENT_BET_CHIP = {
        'log': {
            'type': 'CLIENT_BET_CHIP', 
            'value': {
                    'type': 'Chip', 
                    'amount': 1, 
                    'codes': {'BAC_Player': 1}, 
                    'bets': {'Player': 1}, 
                    'gameType': 'baccarat', 
                    'gameTime': '01:39:14', 
                    'currency': 'USD', 
                    'chipStack': [1, 2, 5, 25, 100, 500], 
                    'tableMinLimit': 1, 
                    'tableMaxLimit': 50000, 
                    'balance': 41.72, 
                    'channel': 'PCMac', 
                    'orientation': 'landscape', 
                    'gameDimensions': {'width': 1066.65625, 'height': 600}, 
                    'gameId': '1802c8c4de8453b1c70d3a20'}
                    }}


BET_RESPONSE = {'id': 'wpu72xakhm', 
                'type': 'baccarat.playerBetRequest', 
                'args': {
                        'gameId': '1802c8c4de8453b1c70d3a20', 
                        'replyId': 'baccarat.playerBetRequest-86568033-1730165964976', 
                        'timestamp': 1730165964976, 
                        'betTags': {
                                'openMwTables': 1, 
                                'mwLayout': 8, 
                                'btTableView': '0', 
                                'orientation': 'landscape'
                                }, 
                        'action': {
                                'name': 'Chips', 
                                'chips': {'Player': 1}
                                }, 
                        'correlationId': 'fc1f8eb1c70d3a44'
                        }
                    }
