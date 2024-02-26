// ScanDialog.cpp : implementation file
//

#include "stdafx.h"
#include "ToolScan.h"
#include "ScanDialog.h"
#include "afxdialogex.h"
#include "ToolScanDlg.h"

#include <algorithm>
#include <iterator>
#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <sstream>
#include <thread>
#pragma warning(disable: 4996)
#pragma comment(lib, "Ws2_32.lib")

// CScanDialog dialog

IMPLEMENT_DYNAMIC(CScanDialog, CDialogEx)

CScanDialog::CScanDialog(CWnd* pParent /*=NULL*/)
	: CDialogEx(CScanDialog::IDD, pParent)
{
	isScanning = false;
}

CScanDialog::~CScanDialog()
{
}

void CScanDialog::DoDataExchange(CDataExchange* pDX)
{
	DragAcceptFiles();
	ModifyStyle(WS_SYSMENU, 0);
	CDialogEx::DoDataExchange(pDX);

	DDX_Control(pDX, IDC_BUTTON_SCAN, m_btnScan);
	DDX_Control(pDX, IDC_LIST1, m_lbPathctl);
	DDX_Control(pDX, IDC_EDIT2, m_editPath);
	DDX_Control(pDX, IDC_LIST2, mLv_log);
}
void CScanDialog::OnDropFiles(HDROP dropInfo)
{
	CString    sFile;
	DWORD      nBuffer = 0;

	UINT nFilesDropped = DragQueryFile(dropInfo, 0xFFFFFFFF, NULL, 0);

	if (nFilesDropped > 0)
	{
		nBuffer = DragQueryFile(dropInfo, 0, NULL, 0);
		DragQueryFile(dropInfo, 0, sFile.GetBuffer(nBuffer + 1), nBuffer + 1);
		bool isDir = (GetFileAttributes(sFile.GetString()) != INVALID_FILE_ATTRIBUTES) ? (GetFileAttributes(sFile.GetString()) & FILE_ATTRIBUTE_DIRECTORY) : false;
		if (isScanning){
			if (!isDir){
				m_lbPathctl.AddString(sFile);
			}
		}
		else
		{
			if (isDir){
				m_lbPathctl.AddString(sFile);
			}
		}
		sFile.ReleaseBuffer();
	}
	DragFinish(dropInfo);
}

BEGIN_MESSAGE_MAP(CScanDialog, CDialogEx)
	ON_WM_DROPFILES()
	ON_BN_CLICKED(IDC_BUTTON_SCAN, &CScanDialog::OnBnClickedButtonScan)
	ON_LBN_DBLCLK(IDC_LIST1, &CScanDialog::OnLbnDblclkList1)
	ON_WM_LBUTTONDOWN()
	ON_WM_MOUSEMOVE()
	ON_WM_LBUTTONUP()
	ON_WM_LBUTTONDBLCLK()
	ON_BN_CLICKED(IDC_BUTTON2, &CScanDialog::OnBnClickedButton2)
END_MESSAGE_MAP()

SOCKET initSocket(){
	WSADATA wsaData;
	SOCKET sock = INVALID_SOCKET;
	struct addrinfo *result = NULL, *ptr = NULL, hints;
	int iResult;

	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		std::cout << "WSAStartup failed: " << iResult << std::endl;
		return INVALID_SOCKET;
	}

	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;

	iResult = getaddrinfo("127.0.0.1", "44444", &hints, &result);
	if (iResult != 0) {
		std::cout << "getaddrinfo failed: " << iResult << std::endl;
		WSACleanup();
		return INVALID_SOCKET;
	}

	for (ptr = result; ptr != NULL; ptr = ptr->ai_next) {
		sock = socket(ptr->ai_family, ptr->ai_socktype, ptr->ai_protocol);
		if (sock == INVALID_SOCKET) {
			std::cout << "socket failed: " << WSAGetLastError() << std::endl;
			WSACleanup();
			return INVALID_SOCKET;
		}

		iResult = connect(sock, ptr->ai_addr, (int)ptr->ai_addrlen);
		if (iResult == SOCKET_ERROR) {
			closesocket(sock);
			sock = INVALID_SOCKET;
			continue;
		}
		break;
	}

	freeaddrinfo(result);

	if (sock == INVALID_SOCKET) {
		std::cout << "Unable to connect to server!" << std::endl;
		WSACleanup();
		return INVALID_SOCKET;
	}
	return sock;
}

void runPythonScript() {
	const char* scriptPath = "main.py";
	std::string commandLine = "pyw -3 ";
	commandLine += scriptPath;
	WCHAR commandLineWCHAR[MAX_PATH];
	mbstowcs(commandLineWCHAR, commandLine.c_str(), MAX_PATH);
	STARTUPINFO si;
	PROCESS_INFORMATION pi;

	ZeroMemory(&si, sizeof(STARTUPINFO));
	si.cb = sizeof(STARTUPINFO);
	ZeroMemory(&pi, sizeof(PROCESS_INFORMATION));
	if (CreateProcess(NULL, commandLineWCHAR, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
		WaitForSingleObject(pi.hProcess, INFINITE);
		CloseHandle(pi.hProcess);
		CloseHandle(pi.hThread);
	}
	else {
		std::cerr << "Error creating process. Error code: " << GetLastError() << std::endl;
	}
}

void InsertItemToListCtrl(CListCtrl& listCtrl, const std::string& filename, const std::string& status, const std::string& datetime_str) {
#ifdef UNICODE
	CString cstrFilename(CA2W(filename.c_str()));
	CString cstrStatus(CA2W(status.c_str()));
	CString cstrDatetimeStr(CA2W(datetime_str.c_str()));
#else
	CString cstrFilename(filename.c_str());
	CString cstrStatus(status.c_str());
	CString cstrDatetimeStr(datetime_str.c_str());
#endif
	int nItemCount = listCtrl.GetItemCount();
	int nItemIndex = -1;
	for (int i = 0; i < nItemCount; ++i) {
		CString strItemText = listCtrl.GetItemText(i, 1);
		if (strItemText == cstrFilename) {
			nItemIndex = i;
			break;
		}
	}
	if (nItemIndex != -1) {
		listCtrl.SetItemText(nItemIndex, 2, cstrStatus);
	}
	else {
		int nIndex = listCtrl.GetItemCount();
		CString strIndex;
		strIndex.Format(_T("%d"), nIndex + 1); 
		listCtrl.InsertItem(nIndex, strIndex);          
		listCtrl.SetItemText(nIndex, 1, cstrFilename);   
		listCtrl.SetItemText(nIndex, 2, cstrStatus);     
		listCtrl.SetItemText(nIndex, 3, cstrDatetimeStr);
	}
}

void CScanDialog::updateDataListView(){
	SOCKET sock = initSocket();
	int iResult;
	char buffer[1024];
	while (true){
		iResult = recv(sock, buffer, 1024, 0);
		if (iResult > 0) {
			std::cout << "Bytes received: " << iResult << std::endl;
			buffer[iResult] = '\0';
			std::cout << buffer << std::endl;
			std::istringstream iss(buffer);
			std::string filename, status, datetime_str;
			char discard_char;
			iss >> discard_char;
			std::getline(iss, filename, ',');
			iss >> discard_char;
			std::getline(iss, status, ',');
			iss >> discard_char;
			std::getline(iss, datetime_str, ')');
			InsertItemToListCtrl(mLv_log, filename, status, datetime_str);
		}
		else if (iResult == 0) {
			std::cout << "Connection closed" << std::endl;
		}
		else {
			std::cout << "recv failed: " << WSAGetLastError() << std::endl;
		}
	}
	closesocket(sock);
	WSACleanup();
}

std::string CStringToString(const CString& cString) {
	return CW2A(cString);
}

void CScanDialog::OnBnClickedButtonScan()
{
	CString urlAV;
	CString urlPDF;
	int maxFilesize;
	CString tokenAPI;
	BOOL sftpMode;
	CString sftpUsername;
	CString sftpPassword;
	CString sftpHost;
	int sftpPort;
	CString sftpRootMapLocal;
	CString szEditPath;

	CToolScanDlg* parentDlg = static_cast<CToolScanDlg*>(GetParent()->GetParent());
	CGenericDialog* tab_Generic = parentDlg->GetTabGenericDlg();
	parentDlg->m_generic.m_eUrlAV.GetWindowTextW(urlAV);
	parentDlg->m_generic.m_eUrlConvert.GetWindowTextW(urlPDF);
	parentDlg->m_generic.m_eMaxfilesize.GetWindowTextW(sftpHost);
	maxFilesize = _ttoi(sftpHost);
	parentDlg->m_generic.m_eTokenApi.GetWindowTextW(tokenAPI);
	parentDlg->m_generic.m_btnMode.GetWindowTextW(sftpHost);
	if (sftpHost == (L"ON")){
		sftpMode = 1;
	}
	else
	{
		sftpMode = 0;
	}
	parentDlg->m_generic.m_eUsername.GetWindowTextW(sftpUsername);
	parentDlg->m_generic.m_ePassword.GetWindowTextW(sftpPassword);
	parentDlg->m_generic.m_eHost.GetWindowTextW(sftpHost);
	parentDlg->m_generic.m_ePort.GetWindowTextW(sftpRootMapLocal);
	sftpPort = _ttoi(sftpRootMapLocal);
	parentDlg->m_generic.m_eRootlocalmap.GetWindowTextW(sftpRootMapLocal);
	m_editPath.GetWindowTextW(sftpHost);
	std::vector<std::pair<std::string, int>> folder_path;

	if (sftpMode == 1){
		m_editPath.GetWindowTextW(szEditPath);
		CT2CA pszConvertedAnsiString(szEditPath);
		std::string strStd(pszConvertedAnsiString);
		std::istringstream iss(strStd);
		std::string token;
		int i = 0;
		while (std::getline(iss, token, ';'))
		{
			token.erase(std::remove_if(token.begin(), token.end(), ::isspace), token.end());
			if (!token.empty())
			{
				token.pop_back();
				folder_path.push_back({ token, i });
				i += 1;
			}
		}
	}
	else
	{
		int itemCount = m_lbPathctl.GetCount();
		for (int i = 0; i < itemCount; i++)
		{
			CString itemText;
			m_lbPathctl.GetText(i, itemText);
			CT2CA pszConvertedAnsiString(itemText);
			std::string strStd(pszConvertedAnsiString);
			folder_path.push_back({ strStd, i + 1 });
		}
	}
	//tab_Generic->m_eUrlAV.GetWindowTextW(urlAV);
	//tab_Generic->GetDlgItemText(IDC_EDIT1, edit1);

	CToolScanDlg::Config myConfig;
	parentDlg->readConfigFromFile(myConfig, "config.ini");
	//parentDlg->updateHostname(myConfig, "new.hostname.com");
	myConfig.settings.URL_avscan = CStringToString(urlAV);
	myConfig.settings.URL_off2pdf = CStringToString(urlPDF);
	myConfig.settings.max_file_size = maxFilesize;
	myConfig.settings.token = CStringToString(tokenAPI);
	myConfig.settings.folder_path.clear();
	myConfig.settings.folder_path = folder_path;
	myConfig.sftp.on_demand = sftpMode ? 1 : 0;
	myConfig.sftp.sftp_folder_path = folder_path;
	myConfig.sftp.root_local_folder = CStringToString(sftpRootMapLocal);
	myConfig.sftp.hostname = CStringToString(sftpHost);
	myConfig.sftp.port = sftpPort;
	myConfig.sftp.username = CStringToString(sftpUsername);
	myConfig.sftp.password = CStringToString(sftpPassword);
	myConfig.virustotal.on_demand = 0;
	myConfig.ai_detect.on_demand = 0;
	//parentDlg->parseFolderPath("[('C:\\Users\\Admin\\Desktop\\TEST_SCANN\\3\\7', 1),('C:\\Users\\Admin\\Desktop\\TEST_SCANN\\foldertest\\2', 2),]", myConfig.settings.folder_path);
	std::ifstream file1("config.ini");
	if (!file1.good()){
		file1.close();
		parentDlg->writeConfigToFile(myConfig, "config.ini");
	}
	file1.close();
	std::thread pythonThread(runPythonScript);
	pythonThread.detach();
	std::thread updateThread(&CScanDialog::updateDataListView, this);
	updateThread.detach();
	
}

std::wstring BrowseFolder()
{
	wchar_t szFolderPath[MAX_PATH] = L"";

	BROWSEINFO bi;
	ZeroMemory(&bi, sizeof(bi));
	bi.hwndOwner = NULL;
	bi.pidlRoot = NULL;
	bi.pszDisplayName = szFolderPath;
	bi.lpszTitle = L"Select a folder";
	bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_USENEWUI;

	LPITEMIDLIST pItem = SHBrowseForFolder(&bi);
	if (pItem != NULL)
	{
		if (SHGetPathFromIDList(pItem, szFolderPath) == TRUE)
		{
			std::wstring selectedFolder(szFolderPath);
			CoTaskMemFree(pItem);
			return selectedFolder;
		}
		else
		{
			CoTaskMemFree(pItem);
		}
	}

	return L"";
}
void CScanDialog::OnLbnDblclkList1()
{
	std::wstring selectedFolderPath = BrowseFolder();
	CString selectedFolder(selectedFolderPath.c_str());
	int ninDex;
	ninDex = m_lbPathctl.GetCurSel();
	m_lbPathctl.InsertString(ninDex, selectedFolder);
	m_lbPathctl.DeleteString(ninDex + 1);
}
void CScanDialog::OnLButtonDown(UINT nFlags, CPoint point)
{
	m_lbPathctl.ScreenToClient(&point);
	m_nDragIndex = m_lbPathctl.ItemFromPoint(point, m_bListBoxItemSel);
	if (m_bListBoxItemSel)
	{
		m_bDragging = TRUE;
		SetCapture(); 
	}

	CDialog::OnLButtonDown(nFlags, point);
}

void CScanDialog::OnMouseMove(UINT nFlags, CPoint point)
{
	if (m_bDragging)
	{
		m_lbPathctl.ScreenToClient(&point);
		m_lbPathctl.SetCaretIndex(m_lbPathctl.ItemFromPoint(point, m_bListBoxItemSel));
		m_lbPathctl.Invalidate();
	}

	CDialog::OnMouseMove(nFlags, point);
}

void CScanDialog::OnLButtonUp(UINT nFlags, CPoint point)
{
	if (m_bDragging)
	{
		m_bDragging = FALSE;
		ReleaseCapture();
		m_lbPathctl.Invalidate();
	}

	CDialog::OnLButtonUp(nFlags, point);
}
void CScanDialog::OnLButtonDblClk(UINT nFlags, CPoint point) {

	CDialog::OnLButtonDblClk(nFlags, point);
}

void CScanDialog::OnBnClickedButton2()
{
	std::wstring selectedFolderPath = BrowseFolder();
	CString selectedFolder(selectedFolderPath.c_str());
	m_lbPathctl.AddString(selectedFolder);
}

BOOL CScanDialog::PreTranslateMessage(MSG* pMsg)
{
	CToolTipCtrl* pToolTip = (((CToolScanDlg*)GetParent()->GetParent())->m_pTooltip);
	if (pToolTip->m_hWnd != NULL)
		pToolTip->RelayEvent(pMsg);
	return CDialogEx::PreTranslateMessage(pMsg);
}

BOOL CScanDialog::OnInitDialog()
{
	CDialogEx::OnInitDialog();
	CDialogEx::OnInitDialog();
	CToolTipCtrl* pToolTip = static_cast<CToolScanDlg*>(GetParent()->GetParent())->m_pTooltip;
	pToolTip->AddTool(&m_btnScan, _T("First Scan Automated, Second to priority file selected"));
	pToolTip->AddTool(GetDlgItem(IDC_BUTTON2), _T("Drag drop, or click file here to upload folder Scan "));
	return TRUE;
}
