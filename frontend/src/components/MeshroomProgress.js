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
    Typography
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { withStyles } from '@material-ui/core/styles';
import GetAppIcon from '@material-ui/icons/GetApp';
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

    isRemovable(row){
        if(row.isRemovable){
            const removeURL = row.removeURL;
            return (
                <TableCell>
                    <a onClick={() => {
                        this.removeResult(removeURL);
                    }} download>
                        <DeleteIcon />
                    </a>
                </TableCell>
            );
        }
        return <TableCell/>;
    }

    isDownloadable(row){
        if(row.status === 100){
            const downloadUrl = row.downloadURL;
            const fileName = `Dataset: ${row.datasets}`;
            return (
                <TableCell>
                    <a onClick={() => {
                        this.downloadResult(downloadUrl, fileName);
                    }} download>
                        <GetAppIcon/>
                    </a>
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
                <Typography variant="h4"> A list of your projects. </Typography>
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

