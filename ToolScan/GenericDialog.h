#pragma once
#include "afxwin.h"


// CGenericDialog dialog

class CGenericDialog : public CDialogEx
{
	DECLARE_DYNAMIC(CGenericDialog)

public:
	CGenericDialog(CWnd* pParent = NULL);   // standard constructor
	virtual ~CGenericDialog();

// Dialog Data
	enum { IDD = IDD_DIALOG_GENERIC };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	DECLARE_MESSAGE_MAP()
public:
	CButton m_btnMode;
	CEdit m_eUrlAV;
	CEdit m_eUrlConvert;
	CEdit m_eMaxfilesize;
	CEdit m_eTokenApi;
	afx_msg void OnBnClickedButtonMode();
	CEdit m_eUsername;
	CEdit m_ePassword;
	CEdit m_eHost;
	CEdit m_ePort;
	CEdit m_eRootlocalmap;
	afx_msg void OnEnChangeEdit6();
};
