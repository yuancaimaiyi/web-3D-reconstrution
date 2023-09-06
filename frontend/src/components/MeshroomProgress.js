import React from 'react';
import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TablePagination,
    TableRow,
    Typography,
    IconButton
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { withStyles } from '@material-ui/core/styles';
import GetAppIcon from '@material-ui/icons/GetApp';
import VisibilityIcon from "@mui/icons-material/Visibility";
import store from "../store/store";
import axios from "axios";

const StyledTableCell = withStyles((theme) => ({
    head: {
        backgroundColor: theme.palette.common.black,
        color: theme.palette.common.white,
    },
    body: {
        fontSize: 14,
    },
}))(TableCell);

const StyledTableRow = withStyles((theme) => ({
    root: {
        '&:nth-of-type(odd)': {
            backgroundColor: theme.palette.action.hover,
        },
    },
}))(TableRow);

class MeshroomProgress extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            columns : [
                {
                    field: 'id',
                    headerName: 'ID',
                    width: 100
                },
                {
                    field: 'datasets',
                    headerName: 'Project',
                    width: 150,
                    editable: true,
                },
                {
                    field: 'status',
                    headerName: 'Status',
                    type: 'number',
                    width: 150,
                    editable: true,
                },
                {
                    field: 'message',
                    headerName: 'Progress',
                    type: 'number',
                    width: 150,
                },
                {
                    field: 'remove',
                    headerName: 'Remove',
                    type: 'number',
                    width: 100,
                },
            ],
            page: 0,
            rowsPerPage: 7
        }
    }

    downloadResult = (downloadUrl, fileName) => {
        const config = {
            headers: {
                'authorization': 'Bearer ' + store.getState().token
            },
            responseType: 'blob'
        }
        axios.get(downloadUrl, config)
            .then((response) => {
                console.log(response.data);
                let archive = response.data; //new Blob([response.data] , {type: 'application/zip'});
                let archiveUrl = URL.createObjectURL(archive);
                let link = document.createElement("a");
                link.href = archiveUrl;
                link.download = `${fileName}.zip`;
                link.click();
                link.remove();
            })
            .catch((err) => {
                console.log(err);
            });
    }

    removeResult = (removeUrl) =>{
        const config = {
            headers: {
                'authorization': 'Bearer ' + store.getState().token
            },
            responseType: 'blob'
        }
        axios.get(removeUrl, config)
            .then((response) => {
                console.log(response.data);
                alert("Project was successfully removed!");
                this.props.handleStatus();
            })
            .catch((err) => {
                console.log(err);
                alert("Project wasn't removed. Something went wrong.");
            });
    }

     // 添加viewResult方法
    viewResult = (viewUrl) =>{
        const config = {
            headers: {
                'authorization': 'Bearer ' + store.getState().token
            },
            responseType: 'json'
        }
        axios.get(viewUrl,config)
             .then((response) => {
            
            console.log('Response data:', response.data);
            const frontendUrl = response.data.frontend_url;
            if (frontendUrl) {
                // 使用 JavaScript 来执行跳转
                // window.location.href =  frontendUrl // 在浏览器中执行跳转
                window.open(frontendUrl, '_blank');  // 新页面
            } else {
                // 如果没有收到有效的 frontend_url，可以显示错误消息或采取其他操作
                alert("Failed to get correct  viewer url.");
            }
        }) 
        .catch((err) => {
            console.log(err);
            alert("Failed to initiate visualization.");
        });
    }

    isRemovable(row){
        if(row.isRemovable){
            const removeURL = row.removeURL;
            return (
                <TableCell>
                    <IconButton onClick={() => {
                        this.removeResult(removeURL);
                    }} download>
                        <DeleteIcon style={{ fontSize: 24, color: 'red' }}/>
                    </IconButton>
                </TableCell>
            );
        }
        return <TableCell/>;
    }

    isDownloadable(row){
        if(row.status === 100){
            const downloadUrl = row.downloadURL;
            const viewUrl = row.viewURL;
            console.log(viewUrl);
            console.log(downloadUrl);
            const fileName = `Dataset: ${row.datasets}`;
            return (
                <TableCell>
                    <IconButton onClick={() => {
                        this.downloadResult(downloadUrl, fileName);
                    }} download>
                        <GetAppIcon style={{ fontSize: 24, color: 'green' }}/>
                    </IconButton>
                    <IconButton onClick={() => {
                         this.viewResult(viewUrl);
                    }} download>
                        <VisibilityIcon  style={{ fontSize: 24, color: 'blue' }}/>
                    </IconButton>
                </TableCell>
            )
        }
        else{
            return (
                <TableCell>
                    {row.message}
                </TableCell>
            )
        }
    }

    handleChangePage = (event, newPage) => {
        this.setState({page: newPage});
    };

    handleChangeRowsPerPage = (event) => {
        this.setState({
            page: 0,
            rowsPerPage: +event.target.value
        })
    };

    render(){
        return (
            <>
                <Typography variant="h4"> Projects: </Typography>
                <Paper elevation={6} style={{ maxHeight: '65vh', width: "100%", overflow: 'auto'}}>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        {this.state.columns.map((column) => (
                                            <StyledTableCell key={column.field} align='left' >
                                                {column.headerName}
                                            </StyledTableCell>
                                        ))}
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {this.props.rows.slice(this.state.page * this.state.rowsPerPage, this.state.page * this.state.rowsPerPage + this.state.rowsPerPage).map(row =>(
                                        <StyledTableRow key={row.id}>
                                            <TableCell>{row.id} </TableCell>
                                            <TableCell>{row.datasets} </TableCell>
                                            <TableCell>{`${row.status}%`} </TableCell>
                                            {this.isDownloadable(row)}
                                            {this.isRemovable(row)}
                                        </StyledTableRow>
                                        ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                        <TablePagination
                            rowsPerPageOptions={[7, 10, 15]}
                            component="div"
                            count={this.props.rows.length}
                            rowsPerPage={this.state.rowsPerPage}
                            page={this.state.page}
                            onPageChange={this.handleChangePage}
                            onRowsPerPageChange={this.handleChangeRowsPerPage}
                        />
                </Paper>
            </>
        );
    }
}

export default MeshroomProgress;

