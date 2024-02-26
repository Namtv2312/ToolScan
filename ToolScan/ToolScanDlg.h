
// ToolScanDlg.h : header file
//

#pragma once
#include "afxcmn.h"
#include "ScanDialog.h"
#include "GenericDialog.h"
#include <fstream>
#include <sstream>
#include <vector>
#include <iostream>

// CToolScanDlg dialog
class CToolScanDlg : public CDialogEx
{
// Construction
public:
	CToolScanDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	enum { IDD = IDD_TOOLSCAN_DIALOG };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support


// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	CTabCtrl tab_Control;
	CScanDialog m_Scan;
	CGenericDialog m_generic;
	CWnd* m_pwndShow;
	afx_msg void OnTcnSelchangeTab1(NMHDR *pNMHDR, LRESULT *pResult);
	CString getTextEdit();
	CGenericDialog* GetTabGenericDlg() { return &m_generic; }
	struct Config {
		struct Settings {
			std::string URL_avscan;
			std::string URL_off2pdf;
			std::vector<std::pair<std::string, int>> folder_path;
			int max_file_size;
			std::string token;
		} settings;

		struct SFTP {
			int on_demand;
			std::vector<std::pair<std::string, int>> sftp_folder_path;
			std::string root_local_folder;
			std::string hostname;
			int port;
			std::string username;
			std::string password;
		} sftp;

		struct VirusTotal {
			int on_demand;
			std::string key;
		} virustotal;

		struct AIDetect {
			int on_demand;
			std::string URL_ai_detect;
			std::string token;
		} ai_detect;
	};
	void updateHostname(Config &config, const std::string &newHostname);
	void parseFolderPath(const std::string &folderPathStr, std::vector<std::pair<std::string, int>> &folderPath);
	void readConfigFromFile(Config &config, const std::string &filename);
	void fillConfig(Config &config);
	void writeConfigToFile(const Config &config, const std::string &filename); 
};
