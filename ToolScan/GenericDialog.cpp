// GenericDialog.cpp : implementation file
//

#include "stdafx.h"
#include "ToolScan.h"
#include "GenericDialog.h"
#include "afxdialogex.h"


// CGenericDialog dialog

IMPLEMENT_DYNAMIC(CGenericDialog, CDialogEx)

CGenericDialog::CGenericDialog(CWnd* pParent /*=NULL*/)
	: CDialogEx(CGenericDialog::IDD, pParent)
{

}

CGenericDialog::~CGenericDialog()
{
}

void CGenericDialog::DoDataExchange(CDataExchange* pDX)
{
	ModifyStyle(WS_SYSMENU, 0);
	CDialogEx::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_BUTTON_MODE, m_btnMode);
	DDX_Control(pDX, IDC_EDIT1, m_eUrlAV);
	DDX_Control(pDX, IDC_EDIT2, m_eUrlConvert);
	DDX_Control(pDX, IDC_EDIT3, m_eMaxfilesize);
	DDX_Control(pDX, IDC_EDIT4, m_eTokenApi);
	DDX_Control(pDX, IDC_EDIT5, m_eUsername);
	DDX_Control(pDX, IDC_EDIT9, m_ePassword);
	DDX_Control(pDX, IDC_EDIT7, m_eHost);
	DDX_Control(pDX, IDC_EDIT6, m_ePort);
	DDX_Control(pDX, IDC_EDIT8, m_eRootlocalmap);
}

BEGIN_MESSAGE_MAP(CGenericDialog, CDialogEx)
	ON_BN_CLICKED(IDC_BUTTON_MODE, &CGenericDialog::OnBnClickedButtonMode)
END_MESSAGE_MAP()


// CGenericDialog message handlers


void CGenericDialog::OnBnClickedButtonMode()
{
	CString strButtonText;
	m_btnMode.GetWindowText(strButtonText);
	if (strButtonText == (L"ON"))
		m_btnMode.SetWindowText(L"OFF");
	else
		m_btnMode.SetWindowText(L"ON");
}
