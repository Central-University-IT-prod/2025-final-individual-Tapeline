FROM grafana/grafana-enterprise

ADD provisioning /etc/grafana/provisioning
ADD dashboards /var/lib/grafana/dashboards

CMD [ "grafana-reporter" ]
