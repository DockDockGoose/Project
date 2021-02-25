"""     XML Logger following the schema outlined in logfile_schema.xsd.
        To validate that the logger functions correctly run:
            xmllint --schema logfile_schema.xsd --noout [logfiletotest].xml    """

"""     Some notes on logging requirements:  
    -   Only log a quoteServer event when you actually hit the quote server; if you are caching 
        stock quotes and you have a cache hit, that can be logged as a systemEvent.
    -   Any field defined as minOccurs="0" is optional eg. the DUMPLOG command requires a filename, 
        but not a stock symbol.
    -   Money should be logged to the cent. Even if the last digit(s) of the number are zeros, they must 
        appear in your log file. All times must be in the standard Unix timestamp format in milliseconds.
    -   The server field is the name you have given to the server which produced that output.               """

""" TODO:
        -   error check commands
        -   server logs commands out of order
        -   optimize printing   """

import sys
from xml.etree import ElementTree, cElementTree
from xml.dom import minidom

auditNum = "1"
root = ElementTree.Element('log')

""" User commands come from the user command files or from manual entries in the students' web forms.   """
def logUserCommand(infoDict):
    userCommand = ElementTree.SubElement(root, 'userCommand')
    ElementTree.SubElement(userCommand, 'timestamp').text = infoDict['timestamp']
    ElementTree.SubElement(userCommand, 'server').text = infoDict['server']
    ElementTree.SubElement(userCommand, 'transactionNum').text = infoDict['transactionNumber']
    ElementTree.SubElement(userCommand, 'command').text = infoDict['command']
    
    if 'user' in infoDict:
        ElementTree.SubElement(userCommand, 'username').text = infoDict['user']
    if 'stockSymbol' in infoDict:
        ElementTree.SubElement(userCommand, 'stockSymbol').text = infoDict['stockSymbol']
    if 'filename' in infoDict:
        ElementTree.SubElement(userCommand, 'filename').text = infoDict['filename']
    if 'amount' in infoDict:
        ElementTree.SubElement(userCommand, 'funds').text = '%.2f' % infoDict['amount']

""" Every hit to the quote server requires a log entry with the results. The price, symbol, 
    username, timestamp and cryptokey are as returned by the quote server.   """
def logQuoteServer(infoDict):
    quoteServer = ElementTree.SubElement(root, 'quoteServer')
    ElementTree.SubElement(quoteServer, 'timestamp').text = infoDict['timestamp']
    ElementTree.SubElement(quoteServer, 'server').text = infoDict['server']
    ElementTree.SubElement(quoteServer, 'transactionNum').text = infoDict['transactionNumber']
    ElementTree.SubElement(quoteServer, 'price').text = infoDict['price']
    ElementTree.SubElement(quoteServer, 'stockSymbol').text = infoDict['stockSymbol']
    ElementTree.SubElement(quoteServer, 'username').text = infoDict['user']
    ElementTree.SubElement(quoteServer, 'quoteServerTime').text = infoDict['quoteServerTime']
    ElementTree.SubElement(quoteServer, 'cryptokey').text = infoDict['cryptokey']

""" Any time a user's account is touched, an account message is printed.  
    Appropriate actions are "add" or "remove".  """
def logAccountTransaction(infoDict):
    accountTransaction = ElementTree.SubElement(root, 'accountTransaction')
    ElementTree.SubElement(accountTransaction, 'timestamp').text = infoDict['timestamp']
    ElementTree.SubElement(accountTransaction, 'server').text = infoDict['server']
    ElementTree.SubElement(accountTransaction, 'transactionNum').text = infoDict['transactionNumber']
    ElementTree.SubElement(accountTransaction, 'action').text = infoDict['command']         #should be add or remove
    ElementTree.SubElement(accountTransaction, 'username').text = infoDict['user']
    ElementTree.SubElement(accountTransaction, 'funds').text = '%.2f' % infoDict['amount']

""" System events can be current user commands, interserver communications, 
    or the execution of previously set triggers.    """
def logSystemEvent(infoDict):
    systemEvent = ElementTree.SubElement(root, 'systemEvent')
    ElementTree.SubElement(systemEvent, 'timestamp').text = infoDict['timestamp']
    ElementTree.SubElement(systemEvent, 'server').text = infoDict['server']
    ElementTree.SubElement(systemEvent, 'transactionNum').text = infoDict['transactionNumber']
    ElementTree.SubElement(systemEvent, 'command').text = infoDict['command']

    if 'user' in infoDict:
        ElementTree.SubElement(systemEvent, 'username').text = infoDict['user']
    if 'stockSymbol' in infoDict:
        ElementTree.SubElement(systemEvent, 'stockSymbol').text = infoDict['stockSymbol']
    if 'filename' in infoDict:
        ElementTree.SubElement(systemEvent, 'filename').text = infoDict['filename']
    if 'amount' in infoDict:
        ElementTree.SubElement(systemEvent, 'funds').text = '%.2f' % infoDict['amount']

""" Error messages contain all the information of user commands, in 
    addition to an optional error message.  """
def logErrorEvent(infoDict):
    errorEvent = ElementTree.SubElement(root, 'errorEvent')
    ElementTree.SubElement(errorEvent, 'timestamp').text = infoDict['timestamp']
    ElementTree.SubElement(errorEvent, 'server').text = infoDict['server']
    ElementTree.SubElement(errorEvent, 'transactionNum').text = infoDict['transactionNumber']
    ElementTree.SubElement(errorEvent, 'command').text = infoDict['command']

    if 'user' in infoDict:
        ElementTree.SubElement(errorEvent, 'username').text = infoDict['user']
    if 'stockSymbol' in infoDict:
        ElementTree.SubElement(errorEvent, 'stockSymbol').text = infoDict['stockSymbol']
    if 'filename' in infoDict:
        ElementTree.SubElement(errorEvent, 'filename').text = infoDict['filename']
    if 'amount' in infoDict:
        ElementTree.SubElement(errorEvent, 'funds').text = '%.2f' % infoDict['amount']
    if 'errorMessage' in infoDict:
        ElementTree.SubElement(errorEvent, 'errorMessage').text = infoDict['errorMessage']

""" Debugging messages contain all the information of user commands, in 
    addition to an optional debug message.  """
def logDebugEvent(infoDict):
    debugEvent = ElementTree.SubElement(root, 'debugEvent')
    ElementTree.SubElement(debugEvent, 'timestamp').text = infoDict['timestamp']
    ElementTree.SubElement(debugEvent, 'server').text = infoDict['server']
    ElementTree.SubElement(debugEvent, 'transactionNum').text = infoDict['transactionNumber']
    ElementTree.SubElement(debugEvent, 'command').text = infoDict['command']

    if 'user' in infoDict:
        ElementTree.SubElement(debugEvent, 'username').text = infoDict['user']
    if 'stockSymbol' in infoDict:
        ElementTree.SubElement(debugEvent, 'stockSymbol').text = infoDict['stockSymbol']
    if 'filename' in infoDict:
        ElementTree.SubElement(debugEvent, 'filename').text = infoDict['filename']
    if 'amount' in infoDict:
        ElementTree.SubElement(debugEvent, 'funds').text = '%.2f' % infoDict['amount']
    if 'debugMessage' in infoDict:
        ElementTree.SubElement(debugEvent, 'debugMessage').text = infoDict['debugMessage']

def prettyPrintLog(element=root):
    auditNum = str(input("Enter user audit number for filename (1 default): ")) or auditNum
    # Relative path from backend/src
    auditFile = '../audit/logs/logfile' + auditNum + '.xml'        
    # Wrap into an ElementTree instance so we can save it as XML
    tree = cElementTree.ElementTree(element)
    # ET.write() doesnt support pretty print so use minidom to prettify XML
    t = minidom.parseString(ElementTree.tostring(element)).toprettyxml()
    xmlTree = ElementTree.ElementTree(ElementTree.fromstring(t))
    xmlTree.write(auditFile, encoding='us-ascii', xml_declaration=True)

logEvents = {
    'userCommand'           :       logUserCommand,
    'quoteServer'           :       logQuoteServer,
    'accountTransaction'    :       logAccountTransaction,
    'systemEvent'           :       logSystemEvent,
    'errorEvent'            :       logErrorEvent,
    'debugEvent'            :       logDebugEvent,
}
