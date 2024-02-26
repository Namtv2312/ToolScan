#pragma once
#include "afxwin.h"
#include "afxcmn.h"


// CScanDialog dialog

class CScanDialog : public CDialogEx
{
	DECLARE_DYNAMIC(CScanDialog)

public:
	CScanDialog(CWnd* pParent = NULL);   // standard constructor
	virtual ~CScanDialog();

// Dialog Data
	enum { IDD = IDD_DIALOG_SCAN };

protected:
	afx_msg void OnDropFiles(HDROP hDropInfo);
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	DECLARE_MESSAGE_MAP()
public:
	CEdit m_CtrlPath;
	afx_msg void OnBnClickedButtonScan();
	CButton m_btnScan;
	CEdit m_editTCtl;
	afx_msg void OnLbnSelchangeList1();
	afx_msg void OnLbnDblclkList1();
	CListBox m_lbPathctl;
	BOOL m_bDragging;
	int m_nDragIndex;
	BOOL m_bListBoxItemSel;
	afx_msg void OnLButtonDown(UINT nFlags, CPoint point);
	afx_msg void OnMouseMove(UINT nFlags, CPoint point);
	afx_msg void OnLButtonUp(UINT nFlags, CPoint point);
	afx_msg void OnLButtonDblClk(UINT nFlags, CPoint point);
	afx_msg void OnBnClickedButton2();
	CEdit m_editPath;
	CListCtrl mLv_log;
	void updateDataListView();
};
