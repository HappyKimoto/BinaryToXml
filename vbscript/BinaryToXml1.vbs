Option Explicit

Class BytesSnipper
	Private varBytesAll	' Keep all bytes of the file

	' Purpose: Populate varBytesAll
	' Input: strFp as file path
	' Effects: varBytesAll will be initialized
	Public Sub LoadFile(ByVal strFp)
		Dim objStream: Set objStream = CreateObject("ADODB.Stream")
		With objStream
			.Open
			.Type = 1	' Const adTypeBinary = 1
			.LoadFromFile(strFp)
			varBytesAll = .Read()
		End With
		Set objStream = Nothing
		WScript.Echo "TypeName(varBytesAll):" & TypeName(varBytesAll) & "; " &  "UBound(varBytesAll):" & UBound(varBytesAll)
	End Sub

	' Purpose: Snip a section of bytes
	' Inputs: ByVal lngOffset as start_pos in MidB()
	' 		  ByVal intSize as num_bytes in Mid()
	' Return: Bytes()
	Public Function varSnip(ByVal lngOffset, ByVal intSize)
		Dim varReturn, i
		ReDim varReturn(-1)
		For i = 0 To intSize - 1
			' AscB
			' Function that returns the byte code which represents a specific character.
			' The AscB function is used with byte data contained in a string.
			' Instead of returning the character code for the first character, AscB returns the first byte.
			' Ascb("A") will return 65
			'
			' MIDB(text, start_num, num_bytes)
			' MIDB returns a specific number of characters from a text string,
			' starting at the position you specify,
			' based on the number of bytes you specify.
			' MIDB counts each double-byte character as 2 when you have enabled the editing of a language
			' that supports DBCS and then set it as the default language.
			' Otherwise, MIDB counts each character as 1.
			'
			' Note: start_num is 1 origin, not 0 origin.
			' Therefore, start_num should inrement by 1.
			ReDim Preserve varReturn(i)
			varReturn(i) = AscB(MidB(varBytesAll, lngOffset + i + 1, 1))
		Next
		varSnip = varReturn
	End Function

End Class

' Purpose: Converts array of bytes to hex string
' Input: ByVal varBytes as array of bytes
' Return: Hex string
Function strBytesToHexString(ByVal varBytes)
	Dim strBytes, i
	ReDim strBytes(UBound(varBytes))
	For i = LBound(varBytes) To UBound(varBytes)
		strBytes(i) = Right("00" & Hex(varBytes(i)), 2)
	Next
	strBytesToHexString = "&H" & Join(strBytes, "")
End Function

' Purpose: Converts array of bytes to hex string
' Input: ByVal varBytes as array of bytes
' Return: Hex string
' Remark: The reading order is reversed from strBytesToHexString for the sake of little endian
Function strBytesToHexStringReversed(ByVal varBytes)
	Dim strBytes, i, j
	ReDim strBytes(UBound(varBytes))
	For i = LBound(varBytes) To UBound(varBytes)
		j = Abs(i - UBound(varBytes))	' i=(0,1,2,3); j=(3,2,1,0)
		strBytes(i) = Right("00" & Hex(varBytes(j)), 2)
	Next
	strBytesToHexStringReversed = "&H" & Join(strBytes, "")
End Function

Sub Main()
	' File paths
    Dim strFpBin: strFpBin = WScript.Arguments(0)
	Dim strFpXml: strFpXml = WScript.Arguments(1)
	Dim strFpOut: strFpOut = strFpBin & ".xml"
	' Load the input file as binary bytes
	Dim objBytesSnipper: Set objBytesSnipper = New BytesSnipper
	objBytesSnipper.LoadFile strFpBin
	' Parse XML setting file
	Dim objDOM, objNode, objNodes, lngPosition, intSize, strDataType, varSnipped
	Set objDOM = CreateObject("Msxml2.DOMDocument.6.0")
    objDOM.Load strFpXml
	Set objNodes = objDOM.SelectNodes("Data/Datum")
	For Each objNode In objNodes
		lngPosition = CLng("&H" & objNode.getAttribute("PositionHex"))
		intSize = CInt(objNode.getAttribute("Size"))
		varSnipped = objBytesSnipper.varSnip(lngPosition, intSize)
		With objNode
			If .getAttribute("Type") = "Integer" Then
				If .getAttribute("Endian") = "Big" Then
					objNode.Text = CLng(strBytesToHexString(varSnipped))
					WScript.echo objNode.Text
				Elseif .getAttribute("Endian") = "Little" Then
					objNode.Text = CLng(strBytesToHexStringReversed(varSnipped))
				End If
			End If
		End With
    Next

	objDOM.Save(strFpOut)

	Set objNode = Nothing
	Set objNodes = Nothing
	Set objDOM = Nothing

End Sub
Main
