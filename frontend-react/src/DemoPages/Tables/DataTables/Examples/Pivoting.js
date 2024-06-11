import React, { Fragment } from "react";
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import { Row, Col, Card, CardBody } from "reactstrap";
import DataTable from 'react-data-table-component';
import PageTitle from "../../../../Layout/AppMain/PageTitle";
import { makeData } from "./utils";
import axios from 'axios';




const API_URL = 'http://localhost:8000/api/appointments/';



export default class DataTableCustomComps extends React.Component {
  constructor() {
    super();
    this.state = {
      data: makeData(),
      appointments: []
    };
  }
  componentDidMount() {
    this.fetchAppointments();
  }

  fetchAppointments() {
      axios   .get(API_URL)
          .then(response => {
              this.setState({ appointments: response.data })
              console.log(response);
          })
          
          .catch(error => {
              console.error('There was an error fetching the appointments!', error);
          });
  }



  render() {
    const { data } = this.state;

    const columns = [
      {
        name: "First Name",
        selector: row => row.firstName,
        sortable: true,
      },
      {
        name: "Last Name",
        id: "lastName",
        selector: row => row.lastName,
        sortable: true,
      },
    
      {
        name: "Age",
        selector: row => row.age,
        sortable: true,
      },
      {
        name: "Status",
        selector: row => row.status,
        sortable: true,
      },
    
      {
        name: "Visits",
        selector: row => row.visits,
        sortable: true,
        },
    ];

    return (
      <Fragment>
        <TransitionGroup>
          <CSSTransition component="div" classNames="TabsAnimation" appear={true}
            timeout={1500} enter={false} exit={false}>
            <div>
              <PageTitle heading="Data Tables"
                subheading="Choose between regular React Bootstrap tables or advanced dynamic ones."
                icon="pe-7s-medal icon-gradient bg-tempting-azure"/>
                <Row>
                  <Col md="12">
                    <Card className="main-card mb-3">
                      <CardBody>
                        <DataTable columns={columns} data={data} selectableRows pagination />
                      </CardBody>
                    </Card>
                  </Col>
                </Row>
            </div>
          </CSSTransition>
        </TransitionGroup>
      </Fragment>
    );
  }
}
