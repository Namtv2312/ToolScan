
// ToolScanDlg.cpp : implementation file
//
#include "stdafx.h"
#include "ToolScan.h"
#include "ToolScanDlg.h"
#include "afxdialogex.h"
#ifdef _DEBUG
#define new DEBUG_NEW
#endif

// CAboutDlg dialog used for App About

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

// Dialog Data
	enum { IDD = IDD_ABOUTBOX };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

// Implementation
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(CAboutDlg::IDD)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// CToolScanDlg dialog



CToolScanDlg::CToolScanDlg(CWnd* pParent /*=NULL*/)
	: CDialogEx(CToolScanDlg::IDD, pParent)
	, m_pwndShow(NULL)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CToolScanDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_TAB1, tab_Control);
}

BEGIN_MESSAGE_MAP(CToolScanDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_NOTIFY(TCN_SELCHANGE, IDC_TAB1, &CToolScanDlg::OnTcnSelchangeTab1)
END_MESSAGE_MAP()


// CToolScanDlg message handlers

BOOL CToolScanDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon

	// TODO: Add extra initialization here
	tab_Control.InsertItem(0, _T("Generic Settings"));
	tab_Control.InsertItem(1, _T("Scan"));

	CRect rect;
	tab_Control.GetClientRect(&rect);
	m_Scan.Create(IDD_DIALOG_SCAN, &tab_Control);
	m_Scan.SetWindowPos(NULL, 5, 25, rect.Width() - 10, rect.Height() - 30, SWP_HIDEWINDOW | SWP_NOZORDER);

	m_generic.Create(IDD_DIALOG_GENERIC, &tab_Control);
	m_generic.SetWindowPos(NULL, 5, 25, rect.Width() - 10, rect.Height() - 30, SWP_SHOWWINDOW | SWP_NOZORDER);
	m_pwndShow = &m_generic;

	CBitmap bmp;
	bmp.Attach((HBITMAP)LoadImage(AfxGetInstanceHandle(), MAKEINTRESOURCE(IDB_PNG_OFF), IMAGE_BITMAP, 0, 0, LR_DEFAULTCOLOR));
	CButton* pButton = (CButton*)m_generic.GetDlgItem(IDC_BUTTON_MODE);
	pButton->ModifyStyle(0, BS_BITMAP | BS_CENTER);
	pButton->SetBitmap(bmp);

	m_Scan.mLv_log.SetExtendedStyle(LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES);
	m_Scan.mLv_log.InsertColumn(0, _T("STT"), LVCFMT_LEFT, 30);
	m_Scan.mLv_log.InsertColumn(1, _T("File Name"), LVCFMT_LEFT, 150);
	m_Scan.mLv_log.InsertColumn(2, _T("Staus"), LVCFMT_LEFT, 80);
	m_Scan.mLv_log.InsertColumn(3, _T("Time Analyze"), LVCFMT_LEFT, 180);

	return TRUE; 
}

void CToolScanDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CToolScanDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

// The system calls this function to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CToolScanDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}



void CToolScanDlg::OnTcnSelchangeTab1(NMHDR *pNMHDR, LRESULT *pResult)
{
	CString sftpHost;
	if (m_pwndShow != NULL){
		m_pwndShow->ShowWindow(SW_HIDE);
		m_pwndShow = NULL;
	}
	int nIndex = tab_Control.GetCurSel();
	switch (nIndex){
	case 0:
		m_generic.ShowWindow(SW_SHOW);
		m_pwndShow = &m_generic;
		break;
	case 1:
		m_generic.m_btnMode.GetWindowTextW(sftpHost);
		if ( sftpHost == L"ON"){
			m_Scan.GetDlgItem(IDC_BUTTON2)->ShowWindow(SW_HIDE);
			m_Scan.GetDlgItem(IDC_LIST1)->ShowWindow(SW_HIDE);
			m_Scan.GetDlgItem(IDC_EDIT2)->ShowWindow(SW_SHOW);
		}
		else
		{
			m_Scan.GetDlgItem(IDC_BUTTON2)->ShowWindow(SW_SHOW);
			m_Scan.GetDlgItem(IDC_LIST1)->ShowWindow(SW_SHOW);
			m_Scan.GetDlgItem(IDC_EDIT2)->ShowWindow(SW_HIDE);
		}
		m_Scan.ShowWindow(SW_SHOW);
		m_pwndShow = &m_Scan;
		break;


	}

	// TODO: Add your control notification handler code here
	*pResult = 0;
}
CString CToolScanDlg::getTextEdit(){
	CString edit1;
	m_generic.m_eUrlAV.GetWindowTextW(edit1);
	return edit1;
}
void CToolScanDlg::updateHostname(Config &config, const std::string &newHostname) {
	config.sftp.hostname = newHostname;
}

void CToolScanDlg::parseFolderPath(const std::string &folderPathStr, std::vector<std::pair<std::string, int>> &folderPath) {
	std::istringstream iss(folderPathStr.substr(1, folderPathStr.size() - 2)); // Remove brackets
	std::string token;
	while (std::getline(iss, token, '(')) {
		if (!token.empty() && token != ", ") {
			size_t pos = token.find_first_of('\'');
			std::string path = token.substr(pos + 1, token.find_last_of('\'') - pos - 1);
			int num = std::stoi(token.substr(token.find_last_of(' ') + 1, token.find_last_of(')') - token.find_last_of(' ') - 1));
			folderPath.push_back({ path, num });
		}
	}
}
void CToolScanDlg::readConfigFromFile(Config &config, const std::string &filename) {
	std::ifstream file(filename);
	std::string line;
	std::string section;

	if (file.is_open()) {
		while (std::getline(file, line)) {
			if (line[0] == '[') {
				section = line.substr(1, line.size() - 2);
			}
			else {
				std::istringstream is_line(line);
				std::string key;
				if (std::getline(is_line, key, '=')) {
					std::string value;
					if (std::getline(is_line, value)) {
						// Trim whitespace
						key.erase(0, key.find_first_not_of(' '));
						key.erase(key.find_last_not_of(' ') + 1);
						value.erase(0, value.find_first_not_of(' '));
						value.erase(value.find_last_not_of(' ') + 1);
						if (section == "Settings" && key == "URL_avscan") {
							config.settings.URL_avscan = value;
						}
						else if (section == "Settings" && key == "URL_off2pdf") {
							config.settings.URL_off2pdf = value;
						}
						else if (section == "Settings" && key == "Folder_path") {
							parseFolderPath(value, config.settings.folder_path);
						}
						else if (section == "Settings" && key == "Max_file_size") {
							config.settings.max_file_size = std::stoi(value);
						}
						else if (section == "Settings" && key == "token") {
							config.settings.token = value;
						}
						else if (section == "sftp" && key == "on_demand") {
							config.sftp.on_demand = std::stoi(value);
						}
						else if (section == "sftp" && key == "sftp_folder_path") {
							parseFolderPath(value, config.sftp.sftp_folder_path);
						}
						else if (section == "sftp" && key == "root_local_folder") {
							config.sftp.root_local_folder = value;
						}
						else if (section == "sftp" && key == "hostname") {
							config.sftp.hostname = value;
						}
						else if (section == "sftp" && key == "port") {
							config.sftp.port = std::stoi(value);
						}
						// Assign value to corresponding field in config
						else if (section == "sftp" && key == "username") {
							config.sftp.username = value;
						}
						else if (section == "sftp" && key == "password") {
							config.sftp.password = value;
						}
					}
				}
			}
		}
		file.close();
	}
	else {
		std::cerr << "Unable to open file: " << filename << std::endl;
	}
}
void CToolScanDlg::fillConfig(Config &config) {
	// Fill in values for the Config struct
	config.settings.URL_avscan = "https://192.168.143.183:8035/scan";
	config.settings.URL_off2pdf = "https://192.168.143.183:8004/upload";
	config.settings.folder_path = { { "C:\\Users\\Admin\\Desktop\\TEST_SCANN\\foldertest\\1", 1 },
	{ "C:\\Users\\Admin\\Desktop\\TEST_SCANN\\foldertest\\2", 2 } };
	config.settings.max_file_size = 10;
	config.settings.token = "abcd@1234";

	config.sftp.on_demand = 0;
	config.sftp.sftp_folder_path = { { R"(C:\Users\IEUser\Desktop\Scan\1)", 1 },
	{ R"(C:\Users\IEUser\Desktop\Scan\2)", 2 } };
	config.sftp.root_local_folder = R"(C:\Users\Admin\Desktop\TEST_SCANN\foldertest\sftp)";
	config.sftp.hostname = "192.168.145.128";
	config.sftp.port = 22;
	config.sftp.username = "ieuser";
	config.sftp.password = "nam4lpha";

	config.virustotal.on_demand = 0;
	config.virustotal.key = "359990a6ffa1c180283eab65975fb6bff1345b94eff44b6e0a194d891618cb5b";

	config.ai_detect.on_demand = 0;
	config.ai_detect.URL_ai_detect = "https://192.168.143.51:8050/scan";
	config.ai_detect.token = "abcd@1234";
}
void CToolScanDlg::writeConfigToFile(const Config &config, const std::string &filename) {
	std::ofstream file(filename);

	if (file.is_open()) {
		file << "[Settings]\n";
		file << "URL_avscan = " << config.settings.URL_avscan << "\n";
		file << "URL_off2pdf = " << config.settings.URL_off2pdf << "\n";
		file << "Folder_path = [";
		for (const auto &path : config.settings.folder_path) {
			file << "(r'" << path.first << "', " << path.second << "),";
		}
		file << "]\n";
		file << "Max_file_size = " << config.settings.max_file_size << "\n";
		file << "token = " << config.settings.token << "\n\n";

		file << "[sftp]\n";
		file << "on_demand = " << config.sftp.on_demand << "\n";
		file << "sftp_folder_path = [";
		for (const auto &path : config.sftp.sftp_folder_path) {
			file << "(r'" << path.first << "', " << path.second << "),";
		}
		file << "]\n";
		file << "root_local_folder = " << config.sftp.root_local_folder << "\n";
		file << "hostname = " << config.sftp.hostname << "\n";
		file << "port = " << config.sftp.port << "\n";
		file << "username = " << config.sftp.username << "\n";
		file << "password = " << config.sftp.password << "\n\n";

		file << "[virustotal]\n";
		file << "on_demand = " << config.virustotal.on_demand << "\n";
		file << "key = " << config.virustotal.key << "\n\n";

		file << "[ai_detect]\n";
		file << "on_demand = " << config.ai_detect.on_demand << "\n";
		file << "URL_ai_detect = " << config.ai_detect.URL_ai_detect << "\n";
		file << "token = " << config.ai_detect.token << "\n";

		file.close();
	}
	else {
		std::cerr << "Unable to open file: " << filename << std::endl;
	}
}
